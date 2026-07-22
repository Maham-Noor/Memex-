import shutil
import sqlite3
from pathlib import Path
from typing import Optional


class SyncService:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or str(Path(__file__).resolve().parents[2] / "memex.db")

    def backup_database(self, destination: str) -> str:
        shutil.copy2(self.db_path, destination)
        return destination

    def ensure_consistency(self) -> None:
        with sqlite3.connect(self.db_path) as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            connection.commit()
