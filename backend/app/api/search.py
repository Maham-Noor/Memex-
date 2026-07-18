from fastapi import APIRouter
from app.core.models.search import SearchRequest, SearchResponse, SearchResult

router = APIRouter(prefix="/search", tags=["search"])

@router.post("/", response_model=SearchResponse)
async def search_capture(request: SearchRequest) -> SearchResponse:
    # TODO: replace mock search with real vector retrieval
    mock_results = [
        SearchResult(
            captureId="example::123",
            title="Example page",
            snippet="This is a mocked search result snippet.",
            url="https://example.com",
            score=0.85,
        )
    ]
    return SearchResponse(status="ok", results=mock_results)
