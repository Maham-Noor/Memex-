from fastapi import APIRouter
from app.core.models.analytics import AnalyticsRequest, AnalyticsResponse

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.post("/", response_model=AnalyticsResponse)
async def analytics_report(request: AnalyticsRequest) -> AnalyticsResponse:
    # TODO: replace mock analytics with actual data aggregation
    summary = {
        "totalCaptures": 0,
        "totalReadTimeSeconds": 0,
        "topDomains": [],
    }
    return AnalyticsResponse(status="ok", summary=summary)
