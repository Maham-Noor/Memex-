from datetime import datetime, timezone
import logging
from typing import List

from app.core.models.capture import CapturePayload, CaptureResponse


class CaptureService:
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self._captures: List[dict] = []

    def receive_capture(self, payload: CapturePayload) -> CaptureResponse:
        self.logger.info("Received capture %s", payload.captureId)
        self._captures.append(payload.dict())
        received_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        return CaptureResponse(
            status="accepted",
            message="Capture received successfully.",
            captureId=payload.captureId,
            receivedAt=received_at,
        )
