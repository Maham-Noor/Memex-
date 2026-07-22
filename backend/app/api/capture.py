from fastapi import APIRouter

from app.core.di import container
from app.core.models.capture import CapturePayload, CaptureResponse

router = APIRouter(prefix="/capture", tags=["capture"])

capture_service = container.capture_service()
processing_service = container.processing_service()

@router.post("/", response_model=CaptureResponse)
async def receive_capture(payload: CapturePayload) -> CaptureResponse:
    processing_service.process_capture(payload)
    return capture_service.receive_capture(payload)
