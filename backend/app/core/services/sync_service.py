import shutil
import sqlite3
from pathlib import Path
from typing import Optional

from app.core.repositories.migration import MigrationManager


class SyncService:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or str(Path(__file__).resolve().parents[2] / "memex.db")
        self.migration_manager = MigrationManager(db_path=self.db_path)
        self.migration_manager.apply_migrations()

    def backup_database(self, destination: str) -> str:
        shutil.copy2(self.db_path, destination)
        return destination

    def verify_recovery(self, backup_path: str) -> bool:
        if not Path(backup_path).exists():
            return False

        with sqlite3.connect(backup_path) as connection:
            row = connection.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='captures'").fetchone()
            return row is not None

    def ensure_consistency(self) -> None:
        with sqlite3.connect(self.db_path) as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            connection.commit()

    def prevent_orphaned_vectors(self) -> None:
        with sqlite3.connect(self.db_path) as connection:
            connection.execute("BEGIN")
            try:
                connection.execute(
                    "DELETE FROM vectors WHERE capture_id NOT IN (SELECT capture_id FROM captures)"
                )
                connection.commit()
            except Exception:
                connection.rollback()
                raise
