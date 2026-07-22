import logging
from pathlib import Path

from app.core.models.analytics import AnalyticsRequest
from app.core.models.capture import CapturePayload
from app.core.repositories.analytics_repository import AnalyticsRepository
from app.core.repositories.capture_repository import CaptureRepository
from app.core.repositories.history_repository import HistoryRepository
from app.core.repositories.settings_repository import SettingsRepository
from app.core.services.analytics_service import AnalyticsService
from app.core.services.capture_service import CaptureService
from app.core.services.sync_service import SyncService
from app.core.services.vector_store_service import VectorStoreService


def test_repository_layer_and_vector_store(tmp_path: Path) -> None:
    db_path = tmp_path / "memex.db"

    capture_repo = CaptureRepository(db_path=str(db_path))
    settings_repo = SettingsRepository(db_path=str(db_path))
    analytics_repo = AnalyticsRepository(db_path=str(db_path))
    history_repo = HistoryRepository(db_path=str(db_path))
    vector_store = VectorStoreService(db_path=str(db_path))
    sync_service = SyncService(db_path=str(db_path))

    payload = CapturePayload(
        captureId="repo-test-1",
        page={"url": "https://example.com", "title": "Example"},
        content="Example content",
        headings=[],
        scrollDepthPercent=50,
        readingDurationSeconds=8,
        timestamps={
            "capturedAt": "2026-07-22T00:00:00Z",
            "sourceCreatedAt": "2026-07-22T00:00:00Z",
            "lastUpdatedAt": "2026-07-22T00:00:00Z",
        },
        finalCapture=True,
    )

    capture_repo.save(payload.captureId, payload.model_dump(), "2026-07-22T00:00:00Z")
    settings_repo.set("capture_settings", {"enabled": True})
    analytics_repo.add_event("capture", {"capture_id": payload.captureId})
    history_repo.add(payload.captureId, payload.model_dump())
    vector_store.upsert(payload.captureId, [0.1, 0.2, 0.3], "general")

    assert capture_repo.get_by_id(payload.captureId) is not None
    assert settings_repo.get("capture_settings")["enabled"] is True
    assert len(analytics_repo.list_events()) == 1
    assert len(history_repo.list()) == 1
    assert vector_store.get(payload.captureId)["category"] == "general"

    backup_path = tmp_path / "memex_backup.db"
    sync_service.backup_database(str(backup_path))
    assert backup_path.exists()


def test_capture_and_analytics_services_use_repositories(tmp_path: Path) -> None:
    db_path = tmp_path / "memex.db"
    capture_service = CaptureService(logger=logging.getLogger("test"), db_path=str(db_path))
    analytics_service = AnalyticsService(logger=logging.getLogger("test"), db_path=str(db_path))

    capture_service.receive_capture(
        CapturePayload(
            captureId="repo-test-2",
            page={"url": "https://news.example.org", "title": "News"},
            content="News content",
            headings=[],
            scrollDepthPercent=70,
            readingDurationSeconds=12,
            timestamps={
                "capturedAt": "2026-07-22T00:00:00Z",
                "sourceCreatedAt": "2026-07-22T00:00:00Z",
                "lastUpdatedAt": "2026-07-22T00:00:00Z",
            },
            finalCapture=True,
        )
    )

    summary = analytics_service.summarize(AnalyticsRequest())
    assert summary.summary["totalCaptures"] == 1
    assert summary.summary["totalReadTimeSeconds"] == 12


def test_sync_service_can_restore_from_backup(tmp_path: Path) -> None:
    db_path = tmp_path / "memex.db"
    backup_path = tmp_path / "memex_backup.db"

    capture_repo = CaptureRepository(db_path=str(db_path))
    payload = CapturePayload(
        captureId="backup-test-1",
        page={"url": "https://example.com", "title": "Example"},
        content="Backup content",
        headings=[],
        scrollDepthPercent=45,
        readingDurationSeconds=9,
        timestamps={
            "capturedAt": "2026-07-22T00:00:00Z",
            "sourceCreatedAt": "2026-07-22T00:00:00Z",
            "lastUpdatedAt": "2026-07-22T00:00:00Z",
        },
        finalCapture=True,
    )
    capture_repo.save(payload.captureId, payload.model_dump(), "2026-07-22T00:00:00Z")

    sync_service = SyncService(db_path=str(db_path))
    sync_service.backup_database(str(backup_path))
    assert sync_service.verify_recovery(str(backup_path)) is True

    restored_repo = CaptureRepository(db_path=str(db_path))
    restored_capture = restored_repo.get_by_id(payload.captureId)
    assert restored_capture is not None
    assert restored_capture["captureId"] == payload.captureId
