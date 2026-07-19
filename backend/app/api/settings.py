from fastapi import APIRouter

from app.core.di import container
from app.core.models.settings import SettingsResponse

router = APIRouter(prefix="/settings", tags=["settings"])

settings_service = container.settings_service()

@router.get("/", response_model=SettingsResponse)
async def get_settings() -> SettingsResponse:
    return SettingsResponse(status="ok", settings=settings_service.get_settings())
