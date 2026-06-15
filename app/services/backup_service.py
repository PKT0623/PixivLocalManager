import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from app.database.artist_repository import ArtistRepository
from app.database.app_setting_repository import AppSettingRepository
from app.database.connection import DATA_DIR


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
                default=self._json_default,
            )

        return file_path

    def export_deleted_artists_backup(
        self,
        artist_ids: list[int],
    ) -> str:
        artists = self.artist_repo.get_by_ids(artist_ids)

        if not artists:
            raise ValueError("백업할 작가 데이터가 없습니다.")

        backup_dir = DATA_DIR / "backups" / "deleted_artists"
        backup_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = backup_dir / f"deleted_artists_{timestamp}.json"

        backup_data: Dict[str, Any] = {
            "backup_type": "deleted_artists",
            "created_at": datetime.now().isoformat(),
            "artist_count": len(artists),
            "artist_ids": artist_ids,
            "artists": artists,
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
                default=self._json_default,
            )

        return str(file_path)

    def restore_deleted_artists_backup(
        self,
        file_path: str,
    ) -> Dict[str, Any]:
        data = self._load_json_file(file_path)

        if data.get("backup_type") != "deleted_artists":
            raise ValueError("삭제 작가 백업 파일이 아닙니다.")

        artists = data.get("artists", [])

        if not isinstance(artists, list):
            raise ValueError("백업 파일의 작가 데이터 형식이 올바르지 않습니다.")

        restored_count = 0
        skipped_count = 0
        skipped_artists = []

        for artist in artists:
            if not isinstance(artist, dict):
                skipped_count += 1
                continue

            pixiv_id = str(artist.get("pixiv_id", "")).strip()

            if not pixiv_id:
                skipped_count += 1
                skipped_artists.append(
                    {
                        "artist_name": artist.get("artist_name", "-"),
                        "pixiv_id": "-",
                        "reason": "Pixiv ID 없음",
                    }
                )
                continue

            existing_artist = self.artist_repo.get_by_pixiv_id(pixiv_id)

            if existing_artist is not None:
                skipped_count += 1
                skipped_artists.append(
                    {
                        "artist_name": artist.get("artist_name", "-"),
                        "pixiv_id": pixiv_id,
                        "reason": "이미 존재",
                    }
                )
                continue

            self.artist_repo.insert_restored_artist(artist)
            restored_count += 1

        self._delete_restored_backup_file(file_path)

        return {
            "restored_count": restored_count,
            "skipped_count": skipped_count,
            "skipped_artists": skipped_artists,
            "total_count": len(artists),
        }

    def import_backup(
        self,
        file_path: str,
    ) -> Dict[str, Any]:
        data = self._load_json_file(file_path)

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
            key = self._get_setting_value(setting, "key")
            value = self._get_setting_value(setting, "value")

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

    def _load_json_file(
        self,
        file_path: str,
    ) -> Dict[str, Any]:
        with open(
            file_path,
            "r",
            encoding="utf-8",
        ) as f:
            data = json.load(f)

        if not isinstance(data, dict):
            raise ValueError("백업 파일 형식이 올바르지 않습니다.")

        return data

    def _delete_restored_backup_file(
        self,
        file_path: str,
    ) -> None:
        path = Path(file_path)

        if not path.exists():
            return

        if not path.is_file():
            return

        path.unlink()

    def _get_setting_value(
        self,
        setting,
        key: str,
    ):
        if isinstance(setting, dict):
            return setting.get(key)

        return getattr(setting, key, None)

    def _json_default(self, value):
        if hasattr(value, "__dict__"):
            return value.__dict__

        return str(value)
