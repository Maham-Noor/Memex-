from fastapi import APIRouter

from app.core.di import container
from app.core.models.search import SearchRequest, SearchResponse

router = APIRouter(prefix="/search", tags=["search"])

search_service = container.search_service()

@router.post("/", response_model=SearchResponse)
async def search_capture(request: SearchRequest) -> SearchResponse:
    return search_service.search(request)
