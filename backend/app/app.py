from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from app.api.analytics import router as analytics_router
from app.api.capture import router as capture_router
from app.api.search import router as search_router
from app.api.settings import router as settings_router
from app.core.config.settings import settings
from app.core.constants import APP_NAME
from app.core.di import container
from app.core.exceptions.handlers import http_exception_handler, generic_exception_handler
from app.core.models.health import HealthResponse
from app.core.utils import build_health_response


logger = container.logger()


def create_app() -> FastAPI:
    app = FastAPI(title=APP_NAME, version=settings.version)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

    app.include_router(capture_router)
    app.include_router(search_router)
    app.include_router(analytics_router)
    app.include_router(settings_router)

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
