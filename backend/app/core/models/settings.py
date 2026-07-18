from pydantic import BaseModel
from typing import Dict, Any


class SettingsResponse(BaseModel):
    status: str
    settings: Dict[str, Any]
