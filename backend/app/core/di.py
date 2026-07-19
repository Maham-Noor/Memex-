from dependency_injector import containers, providers

from app.core.config.settings import settings
from app.core.logging.logger import get_logger
from app.core.services.analytics_service import AnalyticsService
from app.core.services.capture_service import CaptureService
from app.core.services.search_service import SearchService
from app.core.services.settings_service import SettingsService


class Container(containers.DeclarativeContainer):
    config = providers.Object(settings)
    logger = providers.Factory(get_logger, name="memex")
    capture_service = providers.Factory(CaptureService, logger=logger)
    search_service = providers.Factory(SearchService, logger=logger)
    analytics_service = providers.Factory(AnalyticsService, logger=logger)
    settings_service = providers.Factory(SettingsService, logger=logger)


container = Container()
