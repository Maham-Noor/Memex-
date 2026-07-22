import logging
import math
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Optional
from urllib.parse import urlparse

from app.core.models.search import SearchRequest, SearchResponse, SearchResult
from app.core.repositories.capture_repository import CaptureRepository
from app.core.services.processing_service import ProcessingService
from app.core.services.vector_store_service import VectorStoreService


class SearchService:
    def __init__(self, logger: logging.Logger, db_path: Optional[str] = None):
        self.logger = logger
        self.db_path = db_path or str(Path(__file__).resolve().parents[2] / "memex.db")
        self.capture_repository = CaptureRepository(db_path=self.db_path)
        self.vector_store = VectorStoreService(db_path=self.db_path)
        self.processing_service = ProcessingService(logger=logger)

    def _tokenize(self, text: str) -> list[str]:
        return [token for token in re.sub(r"[^a-z0-9]+", " ", text.lower()).split() if token]

    def _embedding_from_text(self, text: str) -> list[float]:
        return self.processing_service.create_embedding(text)

    def _get_query_terms(self, query: str) -> set[str]:
        return set(self._tokenize(query))

    def _matches_filters(self, capture: dict, filters: Optional[dict[str, Any]]) -> bool:
        if not filters:
            return True

        page = capture.get("page", {})
        url = page.get("url", "")
        domain = urlparse(url).netloc.lower()
        content = capture.get("content", "")
        category = self.processing_service.classify_text(content)
        reading_time = capture.get("readingDurationSeconds", 0)
        timestamps = capture.get("timestamps", {})

        if "domain" in filters:
            allowed_domains = {item.lower() for item in filters["domain"] if isinstance(item, str)}
            if allowed_domains and domain not in allowed_domains:
                return False

        if "category" in filters:
            requested_category = filters["category"]
            if requested_category and category != requested_category:
                return False

        if "readingTime" in filters:
            reading_filter = filters["readingTime"]
            if isinstance(reading_filter, dict):
                min_value = reading_filter.get("min")
                max_value = reading_filter.get("max")
                if min_value is not None and reading_time < min_value:
                    return False
                if max_value is not None and reading_time > max_value:
                    return False

        if "date" in filters:
            date_filter = filters["date"]
            if isinstance(date_filter, dict):
                captured_at = timestamps.get("capturedAt", "")
                try:
                    captured_dt = datetime.fromisoformat(captured_at.replace("Z", "+00:00"))
                except ValueError:
                    return False
                if "after" in date_filter:
                    after_dt = datetime.fromisoformat(date_filter["after"].replace("Z", "+00:00"))
                    if captured_dt < after_dt:
                        return False
                if "before" in date_filter:
                    before_dt = datetime.fromisoformat(date_filter["before"].replace("Z", "+00:00"))
                    if captured_dt > before_dt:
                        return False

        return True

    def _cosine_similarity(self, left: list[float], right: list[float]) -> float:
        if not left or not right:
            return 0.0
        dot = sum(a * b for a, b in zip(left, right))
        left_norm = math.sqrt(sum(a * a for a in left))
        right_norm = math.sqrt(sum(b * b for b in right))
        if left_norm == 0 or right_norm == 0:
            return 0.0
        return dot / (left_norm * right_norm)

    def search(self, request: SearchRequest) -> SearchResponse:
        self.logger.info("Search requested for query=%s", request.query)

        query_embedding = self._embedding_from_text(request.query)
        query_terms = self._get_query_terms(request.query)
        captures = self.capture_repository.list_all()
        scored_results = []

        for capture in captures:
            if not self._matches_filters(capture, getattr(request, "filters", None)):
                continue

            content = capture.get("content", "")
            vector_entry = self.vector_store.get(capture.get("captureId", ""))
            payload_embedding = vector_entry.get("embedding") if vector_entry else self._embedding_from_text(content)
            score = self._cosine_similarity(query_embedding, payload_embedding)
            if score <= 0:
                continue

            title = capture.get("page", {}).get("title", "Untitled")
            url = capture.get("page", {}).get("url", "")
            title_terms = self._get_query_terms(title)
            metadata_bonus = 0.05 if query_terms & title_terms else 0.0
            score = round(score + metadata_bonus, 4)

            snippet = content[:180] if content else "Stored capture"
            scored_results.append(
                SearchResult(
                    captureId=capture.get("captureId", "unknown"),
                    title=title,
                    snippet=snippet,
                    url=url,
                    score=score,
                )
            )

        scored_results.sort(key=lambda item: item.score, reverse=True)
        limit = getattr(request, "limit", None) or 10
        return SearchResponse(status="ok", results=scored_results[:limit])
