import logging
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

from app.core.models.analytics import AnalyticsRequest, AnalyticsResponse
from app.core.repositories.capture_repository import CaptureRepository


class AnalyticsService:
    def __init__(self, logger: logging.Logger, db_path: Optional[str] = None):
        self.logger = logger
        self.db_path = db_path or str(Path(__file__).resolve().parents[2] / "memex.db")
        self.repository = CaptureRepository(db_path=self.db_path)

    def summarize(self, request: AnalyticsRequest) -> AnalyticsResponse:
        self.logger.info(
            "Analytics summary requested start=%s end=%s",
            request.startDate,
            request.endDate,
        )
        captures = self.repository.list_all()
        total_read_time_seconds = sum(item.get("readingDurationSeconds", 0) for item in captures)

        domain_counts = {}
        for item in captures:
            page = item.get("page", {})
            domain = page.get("domain")
            if not domain and isinstance(page.get("url"), str):
                parsed = urlparse(page["url"])
                domain = parsed.netloc or parsed.path
            if isinstance(domain, str) and domain:
                domain_counts[domain] = domain_counts.get(domain, 0) + 1

        top_domains = [
            {"domain": domain, "count": count}
            for domain, count in sorted(domain_counts.items(), key=lambda item: item[1], reverse=True)
        ]

        summary = {
            "totalCaptures": len(captures),
            "totalReadTimeSeconds": total_read_time_seconds,
            "topDomains": top_domains,
        }
        return AnalyticsResponse(status="ok", summary=summary)
