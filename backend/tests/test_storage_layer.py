import logging
from pathlib import Path

from app.core.models.analytics import AnalyticsRequest
from app.core.models.capture import CapturePayload
from app.core.services.analytics_service import AnalyticsService
from app.core.services.capture_service import CaptureService


def test_capture_service_persists_payload_to_sqlite(tmp_path: Path) -> None:
    db_path = tmp_path / "memex.db"
    service = CaptureService(logger=logging.getLogger("test"), db_path=str(db_path))

    payload = CapturePayload(
        captureId="storage-test-1",
        page={"url": "https://example.com", "title": "Example"},
        content="Example content for storage test",
        headings=[{"tag": "h1", "text": "Example"}],
        scrollDepthPercent=40,
        readingDurationSeconds=12,
        timestamps={
            "capturedAt": "2026-07-22T00:00:00Z",
            "sourceCreatedAt": "2026-07-22T00:00:00Z",
            "lastUpdatedAt": "2026-07-22T00:00:00Z",
        },
        finalCapture=True,
    )

    response = service.receive_capture(payload)
    stored_capture = service.get_capture(payload.captureId)

    assert response.status == "accepted"
    assert stored_capture is not None
    assert stored_capture["captureId"] == payload.captureId
    assert stored_capture["page"]["url"] == payload.page["url"]


def test_analytics_service_summarizes_stored_captures(tmp_path: Path) -> None:
    db_path = tmp_path / "memex.db"
    capture_service = CaptureService(logger=logging.getLogger("test"), db_path=str(db_path))
    analytics_service = AnalyticsService(logger=logging.getLogger("test"), db_path=str(db_path))

    capture_service.receive_capture(
        CapturePayload(
            captureId="analytics-test-1",
            page={"url": "https://example.com", "title": "Example"},
            content="Example content",
            headings=[],
            scrollDepthPercent=20,
            readingDurationSeconds=10,
            timestamps={
                "capturedAt": "2026-07-22T00:00:00Z",
                "sourceCreatedAt": "2026-07-22T00:00:00Z",
                "lastUpdatedAt": "2026-07-22T00:00:00Z",
            },
            finalCapture=True,
        )
    )
    capture_service.receive_capture(
        CapturePayload(
            captureId="analytics-test-2",
            page={"url": "https://news.example.org", "title": "News"},
            content="More example content",
            headings=[],
            scrollDepthPercent=60,
            readingDurationSeconds=15,
            timestamps={
                "capturedAt": "2026-07-22T00:00:00Z",
                "sourceCreatedAt": "2026-07-22T00:00:00Z",
                "lastUpdatedAt": "2026-07-22T00:00:00Z",
            },
            finalCapture=True,
        )
    )

    response = analytics_service.summarize(AnalyticsRequest())

    assert response.status == "ok"
    assert response.summary["totalCaptures"] == 2
    assert response.summary["totalReadTimeSeconds"] == 25
    assert any(domain["domain"] == "example.com" for domain in response.summary["topDomains"])
