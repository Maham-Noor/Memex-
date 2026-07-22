import json
import sqlite3
from pathlib import Path
from typing import Optional


class CaptureRepository:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or str(Path(__file__).resolve().parents[2] / "memex.db")
        self._initialize()

    def _initialize(self) -> None:
        with sqlite3.connect(self.db_path) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS captures (
                    capture_id TEXT PRIMARY KEY,
                    payload TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            connection.commit()

    def save(self, capture_id: str, payload: dict, created_at: str) -> None:
        with sqlite3.connect(self.db_path) as connection:
            connection.execute(
                "INSERT OR REPLACE INTO captures (capture_id, payload, created_at) VALUES (?, ?, ?)",
                (capture_id, json.dumps(payload), created_at),
            )
            connection.commit()

    def get_by_id(self, capture_id: str) -> Optional[dict]:
        with sqlite3.connect(self.db_path) as connection:
            row = connection.execute(
                "SELECT payload FROM captures WHERE capture_id = ?",
                (capture_id,),
            ).fetchone()

        if row is None:
            return None

        return json.loads(row[0])

    def list_all(self) -> list[dict]:
        with sqlite3.connect(self.db_path) as connection:
            rows = connection.execute("SELECT payload FROM captures").fetchall()

        return [json.loads(row[0]) for row in rows]

    def delete(self, capture_id: str) -> None:
        with sqlite3.connect(self.db_path) as connection:
            connection.execute("DELETE FROM captures WHERE capture_id = ?", (capture_id,))
            connection.commit()
