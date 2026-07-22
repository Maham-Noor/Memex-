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
