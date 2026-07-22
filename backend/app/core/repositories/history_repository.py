import json
import sqlite3
from pathlib import Path
from typing import Optional

from app.core.repositories.migration import MigrationManager


class HistoryRepository:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or str(Path(__file__).resolve().parents[2] / "memex.db")
        self.migration_manager = MigrationManager(db_path=self.db_path)
        self.migration_manager.apply_migrations()

    def add(self, capture_id: str, payload: dict) -> None:
        with sqlite3.connect(self.db_path) as connection:
            connection.execute(
                "INSERT INTO history (capture_id, payload) VALUES (?, ?)",
                (capture_id, json.dumps(payload)),
            )
            connection.commit()

    def list(self) -> list[dict]:
        with sqlite3.connect(self.db_path) as connection:
            rows = connection.execute("SELECT capture_id, payload FROM history").fetchall()

        return [{"capture_id": capture_id, "payload": json.loads(payload)} for capture_id, payload in rows]
