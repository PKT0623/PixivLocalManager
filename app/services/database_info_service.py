from pathlib import Path

from app.database.app_setting_repository import AppSettingRepository
from app.database.artist import ArtistRepository
from app.database.connection import DB_PATH, get_connection
from app.services.backup import DatabaseBackupService


class DatabaseInfoService:
    def __init__(self):
        self.artist_repo = ArtistRepository()
        self.settings_repo = AppSettingRepository()
        self.backup_service = DatabaseBackupService()

    def get_database_info(self) -> dict:
        artists = self.artist_repo.get_all()

        return {
            "db_path": str(DB_PATH),
            "db_size": self._format_bytes(self._get_file_size(DB_PATH)),
            "settings_count": len(self.settings_repo.get_all()),
            "artist_count": len(artists),
            "update_history_count": self._get_update_history_count(),
            "total_artworks": self._sum_artist_value(
                artists,
                "folder_artwork_count",
            ),
            "total_files": self._sum_artist_value(
                artists,
                "folder_file_count",
            ),
            "total_folder_size": self._format_bytes(
                self._sum_artist_value(
                    artists,
                    "folder_size_bytes",
                )
            ),
        }

    def get_program_info(self) -> dict:
        backups = self.backup_service.list_database_backups()

        return {
            "app_name": "Pixiv Local Manager",
            "version": "0.1.0",
            "stack": "Python / PySide6 / SQLite",
            "last_backup_at": (
                self.backup_service.get_last_backup_at_label()
            ),
            "backup_count": len(backups),
            "backup_total_size": (
                self.backup_service.get_backup_total_size_label()
            ),
        }

    def _get_update_history_count(self) -> int:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                "SELECT COUNT(*) FROM artist_update_history"
            )

            row = cursor.fetchone()

            if row is None:
                return 0

            return int(row[0] or 0)

    def _get_file_size(
        self,
        file_path: Path,
    ) -> int:
        if not file_path.exists():
            return 0

        return file_path.stat().st_size

    def _sum_artist_value(
        self,
        artists: list[dict],
        key: str,
    ) -> int:
        total = 0

        for artist in artists:
            try:
                total += int(artist.get(key, 0) or 0)
            except (TypeError, ValueError):
                continue

        return total

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
