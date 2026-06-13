import json
from typing import Dict, Any, List

from app.database.artist_repository import ArtistRepository
from app.database.app_setting_repository import AppSettingRepository


class BackupService:
    def __init__(self):
        self.artist_repo = ArtistRepository()
        self.settings_repo = AppSettingRepository()

    def export_backup(
        self,
        file_path: str,
    ) -> str:
        backup_data: Dict[str, Any] = {
            "artists": self.artist_repo.get_all(),
            "settings": self.settings_repo.get_all(),
        }

        with open(
            file_path,
            "w",
            encoding="utf-8",
        ) as f:
            json.dump(
                backup_data,
                f,
                ensure_ascii=False,
                indent=4,
            )

        return file_path

    def import_backup(
        self,
        file_path: str,
    ) -> Dict[str, Any]:
        with open(
            file_path,
            "r",
            encoding="utf-8",
        ) as f:
            data = json.load(f)

        artists: List[Dict[str, Any]] = data.get(
            "artists",
            [],
        )

        settings: List[Dict[str, Any]] = data.get(
            "settings",
            [],
        )

        for artist in artists:
            self.artist_repo.upsert_artist(artist)

        for setting in settings:
            self.settings_repo.upsert_setting(
                setting["key"],
                setting["value"],
            )

        return {
            "artists_imported": len(artists),
            "settings_imported": len(settings),
        }
