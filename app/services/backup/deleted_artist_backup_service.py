from datetime import datetime
from typing import Any, Dict

from app.database.artist import ArtistRepository
from app.database.connection import DATA_DIR
from .json_utils import BackupJsonUtils


class DeletedArtistBackupService:
    def __init__(self):
        self.artist_repo = ArtistRepository()
        self.json_utils = BackupJsonUtils()

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

        return self.json_utils.save_json_file(
            file_path,
            backup_data,
        )

    def restore_deleted_artists_backup(
        self,
        file_path: str,
    ) -> Dict[str, Any]:
        data = self.json_utils.load_json_file(file_path)

        if data.get("backup_type") != "deleted_artists":
            raise ValueError("삭제 작가 백업 파일이 아닙니다.")

        artists = data.get("artists", [])

        if not isinstance(artists, list):
            raise ValueError("백업 파일의 작가 데이터 형식이 올바르지 않습니다.")

        restore_result = self._restore_artists(artists)

        self.json_utils.delete_file_if_exists(file_path)

        return {
            "restored_count": restore_result["restored_count"],
            "skipped_count": restore_result["skipped_count"],
            "skipped_artists": restore_result["skipped_artists"],
            "total_count": len(artists),
        }

    def _restore_artists(
        self,
        artists: list,
    ) -> dict:
        restored_count = 0
        skipped_count = 0
        skipped_artists = []

        for artist in artists:
            if not isinstance(artist, dict):
                skipped_count += 1
                continue

            skip_reason = self._get_restore_skip_reason(artist)

            if skip_reason is not None:
                skipped_count += 1
                skipped_artists.append(
                    {
                        "artist_name": artist.get("artist_name", "-"),
                        "pixiv_id": self._get_artist_pixiv_id(artist) or "-",
                        "reason": skip_reason,
                    }
                )
                continue

            self.artist_repo.insert_restored_artist(artist)
            restored_count += 1

        return {
            "restored_count": restored_count,
            "skipped_count": skipped_count,
            "skipped_artists": skipped_artists,
        }

    def _get_restore_skip_reason(
        self,
        artist: dict,
    ) -> str | None:
        pixiv_id = self._get_artist_pixiv_id(artist)

        if not pixiv_id:
            return "Pixiv ID 없음"

        existing_artist = self.artist_repo.get_by_pixiv_id(pixiv_id)

        if existing_artist is not None:
            return "이미 존재"

        return None

    def _get_artist_pixiv_id(
        self,
        artist: dict,
    ) -> str:
        return str(artist.get("pixiv_id", "")).strip()
