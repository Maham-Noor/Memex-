import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from app.core.models.capture import CapturePayload, CaptureResponse
from app.core.repositories.capture_repository import CaptureRepository
from app.core.services.processing_service import ProcessingService
from app.core.services.vector_store_service import VectorStoreService


class CaptureService:
    def __init__(self, logger: logging.Logger, db_path: Optional[str] = None):
        self.logger = logger
        self.db_path = db_path or str(Path(__file__).resolve().parents[2] / "memex.db")
        self.repository = CaptureRepository(db_path=self.db_path)
        self.processing_service = ProcessingService(logger=logger)
        self.vector_store = VectorStoreService(db_path=self.db_path)

    def receive_capture(self, payload: CapturePayload) -> CaptureResponse:
        self.logger.info("Received capture %s", payload.captureId)
        received_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self.repository.save(payload.captureId, payload.model_dump(), received_at)

        processing_result = self.processing_service.process_capture(payload)
        embedding = self.processing_service.create_embedding(payload.content)
        self.vector_store.upsert(payload.captureId, embedding, processing_result.category)

        return CaptureResponse(
            status="accepted",
            message="Capture received successfully.",
            captureId=payload.captureId,
            receivedAt=received_at,
        )

    def get_capture(self, capture_id: str) -> Optional[dict]:
        return self.repository.get_by_id(capture_id)
