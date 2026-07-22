import json
import sqlite3
from pathlib import Path
from typing import Optional


class VectorStoreService:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or str(Path(__file__).resolve().parents[2] / "memex.db")
        self._initialize()

    def _initialize(self) -> None:
        with sqlite3.connect(self.db_path) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS vectors (
                    capture_id TEXT PRIMARY KEY,
                    embedding TEXT NOT NULL,
                    category TEXT NOT NULL
                )
                """
            )
            connection.commit()

    def upsert(self, capture_id: str, embedding: list[float], category: str) -> None:
        with sqlite3.connect(self.db_path) as connection:
            connection.execute(
                "INSERT OR REPLACE INTO vectors (capture_id, embedding, category) VALUES (?, ?, ?)",
                (capture_id, json.dumps(embedding), category),
            )
            connection.commit()

    def get(self, capture_id: str) -> Optional[dict]:
        with sqlite3.connect(self.db_path) as connection:
            row = connection.execute(
                "SELECT embedding, category FROM vectors WHERE capture_id = ?",
                (capture_id,),
            ).fetchone()

        if row is None:
            return None

        return {"embedding": json.loads(row[0]), "category": row[1]}

    def delete(self, capture_id: str) -> None:
        with sqlite3.connect(self.db_path) as connection:
            connection.execute("DELETE FROM vectors WHERE capture_id = ?", (capture_id,))
            connection.commit()
