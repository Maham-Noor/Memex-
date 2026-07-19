import logging
from typing import Any, Dict

from app.core.config.settings import settings


class SettingsService:
    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def get_settings(self) -> Dict[str, Any]:
        self.logger.info("Settings requested")
        return {
            "captureEndpoint": "/capture/",
            "searchEndpoint": "/search/",
            "analyticsEndpoint": "/analytics/",
            "searchEnabled": True,
            "analyticsEnabled": True,
            "appName": settings.app_name,
            "version": settings.version,
        }
