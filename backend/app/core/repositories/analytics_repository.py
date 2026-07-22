import json
import sqlite3
from pathlib import Path
from typing import Optional

from app.core.repositories.migration import MigrationManager


class AnalyticsRepository:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or str(Path(__file__).resolve().parents[2] / "memex.db")
        self.migration_manager = MigrationManager(db_path=self.db_path)
        self.migration_manager.apply_migrations()

    def add_event(self, event_type: str, payload: dict) -> None:
        with sqlite3.connect(self.db_path) as connection:
            connection.execute(
                "INSERT INTO analytics_events (event_type, payload) VALUES (?, ?)",
                (event_type, json.dumps(payload)),
            )
            connection.commit()

    def list_events(self) -> list[dict]:
        with sqlite3.connect(self.db_path) as connection:
            rows = connection.execute("SELECT event_type, payload FROM analytics_events").fetchall()

        return [{"event_type": event_type, "payload": json.loads(payload)} for event_type, payload in rows]
