from fastapi import APIRouter
from app.core.models.settings import SettingsResponse

router = APIRouter(prefix="/settings", tags=["settings"])

@router.get("/", response_model=SettingsResponse)
async def get_settings() -> SettingsResponse:
    # TODO: load actual runtime settings from configuration or database
    return SettingsResponse(
        status="ok",
        settings={
            "captureEndpoint": "/capture/",
            "searchEnabled": False,
            "analyticsEnabled": False,
        },
    )
