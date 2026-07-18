import pytest
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_capture_endpoint_accepts_payload():
    payload = {
        "captureId": "test-capture-1",
        "page": {"url": "https://example.com", "title": "Example"},
        "content": "Example content",
        "headings": [{"tag": "h1", "text": "Example"}],
        "scrollDepthPercent": 50,
        "readingDurationSeconds": 10,
        "timestamps": {
            "capturedAt": "2026-07-18T00:00:00Z",
            "sourceCreatedAt": "2026-07-18T00:00:00Z",
            "lastUpdatedAt": "2026-07-18T00:00:00Z",
        },
        "finalCapture": True,
    }

    response = client.post("/capture/", json=payload)

    assert response.status_code == 200
    assert response.json()["status"] == "accepted"
    assert response.json()["captureId"] == payload["captureId"]
