import sqlite3
import time

from app.database.connection import DB_PATH


class DatabaseMaintenanceService:
    def optimize_database(self) -> dict:
        before_size = self._get_database_size()
        started_at = time.perf_counter()

        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("VACUUM")
            conn.execute("ANALYZE")

        elapsed_seconds = time.perf_counter() - started_at
        after_size = self._get_database_size()

        return {
            "before_size": before_size,
            "after_size": after_size,
            "saved_bytes": max(0, before_size - after_size),
            "before_size_label": self._format_bytes(before_size),
            "after_size_label": self._format_bytes(after_size),
            "saved_size_label": self._format_bytes(
                max(0, before_size - after_size)
            ),
            "elapsed_seconds": round(elapsed_seconds, 2),
        }

    def _get_database_size(self) -> int:
        if not DB_PATH.exists():
            return 0

        return DB_PATH.stat().st_size

    def _format_bytes(
        self,
        size_bytes: int,
    ) -> str:
        size = float(size_bytes)

        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size < 1024:
                return f"{size:.1f} {unit}"

            size /= 1024

        return f"{size:.1f} PB"
