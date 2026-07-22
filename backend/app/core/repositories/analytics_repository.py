import json
import sqlite3
from pathlib import Path
from typing import Optional


class AnalyticsRepository:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or str(Path(__file__).resolve().parents[2] / "memex.db")
        self._initialize()

    def _initialize(self) -> None:
        with sqlite3.connect(self.db_path) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS analytics_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    payload TEXT NOT NULL
                )
                """
            )
            connection.commit()

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
