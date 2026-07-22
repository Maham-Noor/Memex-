import logging
from pathlib import Path

from fastapi.testclient import TestClient

from app.core.models.capture import CapturePayload
from app.core.services.capture_service import CaptureService
from app.core.services.search_service import SearchService
from app.main import app

client = TestClient(app)


def test_search_endpoint_returns_results():
    response = client.post("/search/", json={"query": "example"})
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert isinstance(response.json()["results"], list)


def test_search_service_returns_stored_capture_by_similarity(tmp_path: Path) -> None:
    db_path = tmp_path / "memex.db"
    capture_service = CaptureService(logger=logging.getLogger("test"), db_path=str(db_path))
    capture_service.receive_capture(
        CapturePayload(
            captureId="semantic-search-1",
            page={"url": "https://example.com/ai", "title": "AI article"},
            content="This article discusses machine learning and neural networks for modern applications.",
            headings=[],
            scrollDepthPercent=80,
            readingDurationSeconds=20,
            timestamps={
                "capturedAt": "2026-07-22T00:00:00Z",
                "sourceCreatedAt": "2026-07-22T00:00:00Z",
                "lastUpdatedAt": "2026-07-22T00:00:00Z",
            },
            finalCapture=True,
        )
    )

    search_service = SearchService(logger=logging.getLogger("test"), db_path=str(db_path))
    response = search_service.search(type("Request", (), {"query": "neural networks", "filters": None, "limit": 5})())

    assert response.status == "ok"
    assert len(response.results) >= 1
    assert response.results[0].captureId == "semantic-search-1"


def test_search_service_parses_natural_language_filters(tmp_path: Path) -> None:
    db_path = tmp_path / "memex.db"
    capture_service = CaptureService(logger=logging.getLogger("test"), db_path=str(db_path))
    capture_service.receive_capture(
        CapturePayload(
            captureId="nlp-search-1",
            page={"url": "https://news.example.org/tech", "title": "Tech news"},
            content="This is a tech news article about recent AI developments.",
            headings=[],
            scrollDepthPercent=60,
            readingDurationSeconds=15,
            timestamps={
                "capturedAt": "2026-07-21T00:00:00Z",
                "sourceCreatedAt": "2026-07-21T00:00:00Z",
                "lastUpdatedAt": "2026-07-21T00:00:00Z",
            },
            finalCapture=True,
        )
    )

    search_service = SearchService(logger=logging.getLogger("test"), db_path=str(db_path))
    response = search_service.search(
        type(
            "Request",
            (),
            {"query": "find news from news.example.org from last week", "filters": None, "limit": 5},
        )()
    )

    assert response.status == "ok"
    assert len(response.results) >= 1
    assert response.results[0].captureId == "nlp-search-1"
