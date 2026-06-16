from typing import Any, Dict, List

from app.database.app_setting_repository import AppSettingRepository
from app.database.artist import ArtistRepository
from .deleted_artist_backup_service import DeletedArtistBackupService
from .json_utils import BackupJsonUtils


class BackupService:
    def __init__(self):
        self.artist_repo = ArtistRepository()
        self.settings_repo = AppSettingRepository()
        self.json_utils = BackupJsonUtils()
        self.deleted_artist_backup_service = DeletedArtistBackupService()

    def export_backup(
        self,
        file_path: str,
    ) -> str:
        backup_data: Dict[str, Any] = {
            "artists": self.artist_repo.get_all(),
            "settings": self.settings_repo.get_all(),
        }

        return self.json_utils.save_json_file(
            file_path,
            backup_data,
        )

    def export_deleted_artists_backup(
        self,
        artist_ids: list[int],
    ) -> str:
        return (
            self.deleted_artist_backup_service
            .export_deleted_artists_backup(artist_ids)
        )

    def restore_deleted_artists_backup(
        self,
        file_path: str,
    ) -> Dict[str, Any]:
        return (
            self.deleted_artist_backup_service
            .restore_deleted_artists_backup(file_path)
        )

    def import_backup(
        self,
        file_path: str,
    ) -> Dict[str, Any]:
        data = self.json_utils.load_json_file(file_path)

        artists: List[Dict[str, Any]] = data.get(
            "artists",
            [],
        )

        settings = data.get(
            "settings",
            [],
        )

        for artist in artists:
            self.artist_repo.upsert_artist(artist)

        for setting in settings:
            key = self.json_utils.get_setting_value(setting, "key")
            value = self.json_utils.get_setting_value(setting, "value")

            if key is None or value is None:
                continue

            self.settings_repo.set(
                str(key),
                str(value),
            )

        return {
            "artists_imported": len(artists),
            "settings_imported": len(settings),
        }
