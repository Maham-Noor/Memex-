from pydantic import BaseModel
from typing import Any, Dict, List


class CapturePayload(BaseModel):
    captureId: str
    page: Dict[str, Any]
    content: str
    headings: List[Dict[str, Any]]
    scrollDepthPercent: int
    readingDurationSeconds: int
    timestamps: Dict[str, str]
    finalCapture: bool


class CaptureResponse(BaseModel):
    status: str
    message: str
    captureId: str
    receivedAt: str
