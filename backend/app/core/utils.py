from app.core.models.health import HealthResponse


def build_health_response(status: str, message: str, name: str, version: str) -> HealthResponse:
    return HealthResponse(status=status, message=message, name=name, version=version)
