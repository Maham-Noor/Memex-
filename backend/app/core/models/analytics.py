from pydantic import BaseModel
from typing import Dict, Any, Optional


class AnalyticsRequest(BaseModel):
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None


class AnalyticsResponse(BaseModel):
    status: str
    summary: Dict[str, Any]
