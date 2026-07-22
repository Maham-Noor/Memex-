from app.core.services.processing_service import ProcessingService
from app.core.models.capture import CapturePayload


def test_processing_service_normalizes_and_chunks_text():
    service = ProcessingService(logger=None)
    payload = CapturePayload(
        captureId="test-capture-2",
        page={"url": "https://example.com", "title": "Example"},
        content="This is a sentence.  This is another sentence!\nNew line here.",
        headings=[{"tag": "h1", "text": "Example"}],
        scrollDepthPercent=10,
        readingDurationSeconds=20,
        timestamps={
            "capturedAt": "2026-07-18T00:00:00Z",
            "sourceCreatedAt": "2026-07-18T00:00:00Z",
            "lastUpdatedAt": "2026-07-18T00:00:00Z",
        },
        finalCapture=True,
    )

    result = service.process_capture(payload)

    assert result.captureId == payload.captureId
    assert result.chunkCount >= 1
    assert all(chunk.text for chunk in result.chunks)
    assert all(len(chunk.embedding) > 0 for chunk in result.chunks)


def test_processing_service_handles_multiple_webpages():
    service = ProcessingService(logger=None)

    payloads = [
        CapturePayload(
            captureId="test-capture-3",
            page={"url": "https://research.example.com", "title": "Research Article"},
            content="This research article explains data models and study findings.",
            headings=[{"tag": "h1", "text": "Research"}],
            scrollDepthPercent=30,
            readingDurationSeconds=45,
            timestamps={
                "capturedAt": "2026-07-18T01:00:00Z",
                "sourceCreatedAt": "2026-07-18T01:00:00Z",
                "lastUpdatedAt": "2026-07-18T01:00:00Z",
            },
            finalCapture=True,
        ),
        CapturePayload(
            captureId="test-capture-4",
            page={"url": "https://news.example.com", "title": "Daily News"},
            content="Breaking news update: economy and market price changes.",
            headings=[{"tag": "h1", "text": "News"}],
            scrollDepthPercent=60,
            readingDurationSeconds=25,
            timestamps={
                "capturedAt": "2026-07-18T02:00:00Z",
                "sourceCreatedAt": "2026-07-18T02:00:00Z",
                "lastUpdatedAt": "2026-07-18T02:00:00Z",
            },
            finalCapture=True,
        ),
    ]

    results = [service.process_capture(payload) for payload in payloads]

    assert len(results) == 2
    assert results[0].category == "research"
    assert results[1].category == "news"
    assert all(result.chunkCount >= 1 for result in results)
