from typing import Any, Dict, List

from app.database.app_setting_repository import AppSettingRepository
from app.database.artist import ArtistRepository
from app.services.settings_service import SettingsService

from .deleted_artist_backup_service import DeletedArtistBackupService
from .json_utils import BackupJsonUtils


class BackupService:
    def __init__(self):
        self.artist_repo = ArtistRepository()
        self.settings_repo = AppSettingRepository()
        self.settings_service = SettingsService()
        self.json_utils = BackupJsonUtils()
        self.deleted_artist_backup_service = DeletedArtistBackupService()

    def export_backup(
        self,
        file_path: str,
    ) -> str:
        backup_data: Dict[str, Any] = {
            "backup_type": "full_backup",
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

        artists = data.get(
            "artists",
            [],
        )
        settings = data.get(
            "settings",
            [],
        )

        if not isinstance(artists, list):
            raise ValueError("백업 파일의 작가 데이터 형식이 올바르지 않습니다.")

        if not isinstance(settings, list):
            raise ValueError("백업 파일의 설정 데이터 형식이 올바르지 않습니다.")

        artist_result = self._import_artists(artists)
        setting_result = self._import_settings(settings)

        return {
            "artists_imported": artist_result["imported_count"],
            "artists_skipped": artist_result["skipped_count"],
            "settings_imported": setting_result["imported_count"],
            "settings_skipped": setting_result["skipped_count"],
        }

    def _import_artists(
        self,
        artists: List[Dict[str, Any]],
    ) -> dict:
        imported_count = 0
        skipped_count = 0

        for artist in artists:
            if not isinstance(artist, dict):
                skipped_count += 1
                continue

            try:
                self.artist_repo.upsert_artist(artist)
            except (KeyError, TypeError, ValueError):
                skipped_count += 1
                continue

            imported_count += 1

        return {
            "imported_count": imported_count,
            "skipped_count": skipped_count,
        }

    def _import_settings(
        self,
        settings: list,
    ) -> dict:
        imported_count = 0
        skipped_count = 0

        for setting in settings:
            key = self.json_utils.get_setting_value(setting, "key")
            value = self.json_utils.get_setting_value(setting, "value")

            if key is None or value is None:
                skipped_count += 1
                continue

            key = str(key).strip()

            if not key:
                skipped_count += 1
                continue

            self.settings_service.set_setting(
                key,
                value,
            )
            imported_count += 1

        return {
            "imported_count": imported_count,
            "skipped_count": skipped_count,
        }
