from fastapi import APIRouter

from app.core.di import container
from app.core.models.analytics import AnalyticsRequest, AnalyticsResponse

router = APIRouter(prefix="/analytics", tags=["analytics"])

analytics_service = container.analytics_service()

@router.post("/", response_model=AnalyticsResponse)
async def analytics_report(request: AnalyticsRequest) -> AnalyticsResponse:
    return analytics_service.summarize(request)
