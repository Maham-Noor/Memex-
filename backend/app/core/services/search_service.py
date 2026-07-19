import logging

from app.core.models.search import SearchRequest, SearchResponse, SearchResult


class SearchService:
    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def search(self, request: SearchRequest) -> SearchResponse:
        self.logger.info("Search requested for query=%s", request.query)
        results = [
            SearchResult(
                captureId="example::123",
                title="Example page",
                snippet="This is a mocked search result snippet.",
                url="https://example.com",
                score=0.85,
            )
        ]
        return SearchResponse(status="ok", results=results)
