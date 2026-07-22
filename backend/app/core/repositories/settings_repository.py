import json
import sqlite3
from pathlib import Path
from typing import Optional


class SettingsRepository:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or str(Path(__file__).resolve().parents[2] / "memex.db")
        self._initialize()

    def _initialize(self) -> None:
        with sqlite3.connect(self.db_path) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
                """
            )
            connection.commit()

    def set(self, key: str, value: dict) -> None:
        with sqlite3.connect(self.db_path) as connection:
            connection.execute(
                "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
                (key, json.dumps(value)),
            )
            connection.commit()

    def get(self, key: str) -> Optional[dict]:
        with sqlite3.connect(self.db_path) as connection:
            row = connection.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()

        if row is None:
            return None

        return json.loads(row[0])
