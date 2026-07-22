import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from app.core.models.capture import CapturePayload, CaptureResponse
from app.core.repositories.capture_repository import CaptureRepository


class CaptureService:
    def __init__(self, logger: logging.Logger, db_path: Optional[str] = None):
        self.logger = logger
        self.db_path = db_path or str(Path(__file__).resolve().parents[2] / "memex.db")
        self.repository = CaptureRepository(db_path=self.db_path)

    def receive_capture(self, payload: CapturePayload) -> CaptureResponse:
        self.logger.info("Received capture %s", payload.captureId)
        received_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self.repository.save(payload.captureId, payload.model_dump(), received_at)

        return CaptureResponse(
            status="accepted",
            message="Capture received successfully.",
            captureId=payload.captureId,
            receivedAt=received_at,
        )

    def get_capture(self, capture_id: str) -> Optional[dict]:
        return self.repository.get_by_id(capture_id)
