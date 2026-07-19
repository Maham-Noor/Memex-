import logging

from app.core.models.analytics import AnalyticsRequest, AnalyticsResponse


class AnalyticsService:
    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def summarize(self, request: AnalyticsRequest) -> AnalyticsResponse:
        self.logger.info(
            "Analytics summary requested start=%s end=%s",
            request.startDate,
            request.endDate,
        )
        summary = {
            "totalCaptures": 0,
            "totalReadTimeSeconds": 0,
            "topDomains": [],
        }
        return AnalyticsResponse(status="ok", summary=summary)
