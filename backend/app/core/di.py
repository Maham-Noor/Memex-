from dependency_injector import containers, providers

from app.core.config.settings import settings
from app.core.logging.logger import get_logger


class Container(containers.DeclarativeContainer):
    config = providers.Object(settings)
    logger = providers.Factory(get_logger, name="memex")


container = Container()
