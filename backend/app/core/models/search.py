from pydantic import BaseModel
from typing import Any, Dict, List, Optional


class SearchRequest(BaseModel):
    query: str
    filters: Optional[Dict[str, Any]] = None
    limit: Optional[int] = 10


class SearchResult(BaseModel):
    captureId: str
    title: str
    snippet: str
    url: str
    score: float


class SearchResponse(BaseModel):
    status: str
    results: List[SearchResult]
