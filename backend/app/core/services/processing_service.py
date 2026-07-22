import hashlib
import logging
import re
from collections import Counter
from typing import List, Optional

from app.core.models.capture import CapturePayload
from app.core.models.processing import ContentChunk, ProcessingResult


class ProcessingService:
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)

    def normalize_text(self, text: str) -> str:
        text = re.sub(r"<[^>]+>", " ", text)
        text = text.strip()
        text = re.sub(r"\s+", " ", text)
        return text

    def chunk_text(self, text: str, max_chunk_tokens: int = 150) -> List[str]:
        sentences = re.split(r"(?<=[\.\?\!])\s+", text)
        chunks = []
        current_chunk = []
        current_length = 0

        for sentence in sentences:
            token_count = len(sentence.split())
            if current_length + token_count > max_chunk_tokens and current_chunk:
                chunks.append(" ".join(current_chunk).strip())
                current_chunk = []
                current_length = 0

            current_chunk.append(sentence)
            current_length += token_count

        if current_chunk:
            chunks.append(" ".join(current_chunk).strip())

        return chunks

    def generate_chunk_id(self, capture_id: str, chunk_index: int, chunk_text: str) -> str:
        digest = hashlib.sha256(f"{capture_id}:{chunk_index}:{chunk_text}".encode("utf-8")).hexdigest()
        return f"{capture_id}::{digest[:16]}"

    def classify_text(self, text: str) -> str:
        lower = text.lower()
        if "research" in lower or "study" in lower or "science" in lower:
            return "research"
        if "news" in lower or "update" in lower or "article" in lower:
            return "news"
        if "shopping" in lower or "buy" in lower or "price" in lower:
            return "shopping"
        return "general"

    def create_embedding(self, text: str) -> List[float]:
        normalized = self.normalize_text(text)
        tokens = [token for token in re.findall(r"[a-z0-9]+", normalized.lower()) if token]
        if not tokens:
            return [0.0]

        counts = Counter(tokens)
        embedding = [float(counts[token]) for token in sorted(counts.keys())[:64]]
        while len(embedding) < 64:
            embedding.append(0.0)
        return embedding

    def process_capture(self, payload: CapturePayload) -> ProcessingResult:
        normalized = self.normalize_text(payload.content)
        self.logger.info("Processing capture %s: %d chars", payload.captureId, len(normalized))

        text_chunks = self.chunk_text(normalized)
        chunks = []

        for idx, chunk_text in enumerate(text_chunks):
            chunk_id = self.generate_chunk_id(payload.captureId, idx, chunk_text)
            category = self.classify_text(chunk_text)
            embedding = self.create_embedding(chunk_text)
            chunks.append(
                ContentChunk(
                    chunkId=chunk_id,
                    text=chunk_text,
                    tokenCount=len(chunk_text.split()),
                    embedding=embedding,
                    category=category,
                )
            )

        category = self.classify_text(normalized)
        return ProcessingResult(
            captureId=payload.captureId,
            category=category,
            chunkCount=len(chunks),
            chunks=chunks,
        )
