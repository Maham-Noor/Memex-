from fastapi import APIRouter

from app.core.di import container
from app.core.models.capture import CapturePayload, CaptureResponse

router = APIRouter(prefix="/capture", tags=["capture"])

capture_service = container.capture_service()

@router.post("/", response_model=CaptureResponse)
async def receive_capture(payload: CapturePayload) -> CaptureResponse:
    return capture_service.receive_capture(payload)
