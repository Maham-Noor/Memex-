from datetime import datetime, timezone
from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/capture", tags=["capture"])

class CapturePayload(BaseModel):
    captureId: str
    page: Dict[str, Any]
    content: str
    headings: list[Dict[str, Any]]
    scrollDepthPercent: int
    readingDurationSeconds: int
    timestamps: Dict[str, str]
    finalCapture: bool

class CaptureResponse(BaseModel):
    status: str
    message: str
    captureId: str
    receivedAt: str

@router.post("/", response_model=CaptureResponse)
async def receive_capture(payload: CapturePayload) -> CaptureResponse:
    try:
        received_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        # TODO: persist capture or forward to the memory pipeline.
        return CaptureResponse(
            status="accepted",
            message="Capture received successfully.",
            captureId=payload.captureId,
            receivedAt=received_at,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
