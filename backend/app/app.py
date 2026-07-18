from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from app.core.config.settings import settings
from app.core.constants import APP_NAME
from app.core.di import container
from app.core.exceptions.handlers import http_exception_handler, generic_exception_handler
from app.core.models.health import HealthResponse
from app.core.utils import build_health_response


logger = container.logger()


def create_app() -> FastAPI:
    app = FastAPI(title=APP_NAME, version=settings.version)

    app.add_exception_handler(RequestValidationError, http_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)

    @app.get("/health", response_model=HealthResponse)
    async def health_check() -> HealthResponse:
        logger.info("Health check requested")
        return build_health_response(
            status="ok",
            message="Memex backend is healthy.",
            name=settings.app_name,
            version=settings.version,
        )

    return app
