import json
import sqlite3
from pathlib import Path
from typing import Optional

from app.core.repositories.migration import MigrationManager


class VectorStoreService:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or str(Path(__file__).resolve().parents[2] / "memex.db")
        self.migration_manager = MigrationManager(db_path=self.db_path)
        self.migration_manager.apply_migrations()

    def upsert(self, capture_id: str, embedding: list[float], category: str) -> None:
        with sqlite3.connect(self.db_path) as connection:
            connection.execute("BEGIN")
            try:
                connection.execute(
                    "INSERT OR REPLACE INTO vectors (capture_id, embedding, category) VALUES (?, ?, ?)",
                    (capture_id, json.dumps(embedding), category),
                )
                connection.commit()
            except Exception:
                connection.rollback()
                raise

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
            connection.execute("BEGIN")
            try:
                connection.execute("DELETE FROM vectors WHERE capture_id = ?", (capture_id,))
                connection.commit()
            except Exception:
                connection.rollback()
                raise
