from typing import Optional

from app.database.artist_repository import ArtistRepository
from app.services.artist_scan_service import ArtistScanService
from app.services.artist_update_service import ArtistUpdateService
from app.services.artwork_status_service import ArtworkStatusService
from app.services.backup_service import BackupService
from app.services.folder_scan_service import FolderScanService


class ArtistService:
    def __init__(self):
        self.repo = ArtistRepository()
        self.scan_service = ArtistScanService()
        self.update_service = ArtistUpdateService()
        self.backup_service = BackupService()
        self.folder_scanner = FolderScanService()
        self.status_service = ArtworkStatusService()

    def create_artist(
        self,
        folder_path: str,
        rating: int = 0,
        memo: Optional[str] = None,
    ):
        result = self.save_scanned_artist(
            folder_path=folder_path,
            rating=rating,
            memo=memo,
        )

        artist = result.get("artist")

        if artist is None:
            return None

        return artist.get("id")

    def save_scanned_artist(
        self,
        folder_path: str,
        rating: int = 0,
        memo: Optional[str] = None,
    ):
        return self.scan_service.save_scanned_artist(
            folder_path=folder_path,
            rating=rating,
            memo=memo,
        )

    def rescan_artist_folder(
        self,
        artist_id: int,
    ):
        return self.scan_service.rescan_artist_folder(
            artist_id=artist_id,
        )

    def change_artist_folder(
        self,
        artist_id: int,
        folder_path: str,
    ) -> dict:
        artist = self.repo.get_by_id(artist_id)

        if artist is None:
            raise ValueError("작가를 찾을 수 없습니다.")

        scan_result = self.folder_scanner.scan_folder(folder_path)
        pixiv_id = str(scan_result.pixiv_id or "").strip()

        if not pixiv_id:
            raise ValueError("새 폴더에서 Pixiv ID를 찾을 수 없습니다.")

        existing_artist = self.repo.get_by_pixiv_id(pixiv_id)

        if (
            existing_artist is not None
            and int(existing_artist["id"]) != int(artist_id)
        ):
            raise ValueError(
                "같은 Pixiv ID를 가진 작가가 이미 등록되어 있습니다."
            )

        status_result = self.status_service.calculate_status(
            scan_result.local_latest_artwork_ids,
            artist.get("pixiv_latest_artwork_ids", ""),
        )

        update_data = dict(artist)
        update_data["artist_name"] = scan_result.artist_name
        update_data["pixiv_id"] = pixiv_id
        update_data["folder_path"] = scan_result.folder_path
        update_data["folder_size_bytes"] = scan_result.folder_size_bytes
        update_data["folder_file_count"] = scan_result.folder_file_count
        update_data["folder_artwork_count"] = scan_result.folder_artwork_count
        update_data["local_latest_artwork_ids"] = (
            scan_result.local_latest_artwork_ids
        )
        update_data["update_status"] = status_result.status

        self.repo.update_artist(
            artist_id,
            update_data,
        )

        return self.repo.get_by_id(artist_id)

    def check_artist_update(
        self,
        artist_id: int,
    ) -> dict:
        return self.update_service.check_artist_update(
            artist_id=artist_id,
        )

    def check_all_artist_updates(
        self,
        max_count: int = ArtistUpdateService.MAX_BULK_UPDATE_COUNT,
        skip_recent: bool = True,
    ) -> list[dict]:
        return self.update_service.check_all_artist_updates(
            max_count=max_count,
            skip_recent=skip_recent,
        )

    def get_artist(self, artist_id: int):
        return self.repo.get_by_id(artist_id)

    def get_all_artists(self):
        return self.repo.get_all()

    def update_artist(
        self,
        artist_id: int,
        update_data: dict,
    ):
        return self.repo.update_artist(
            artist_id,
            update_data,
        )

    def update_artist_metadata(
        self,
        artist_id: int,
        is_favorite: bool | None = None,
        is_hidden: bool | None = None,
        artist_tags: str | None = None,
    ):
        artist = self.repo.get_by_id(artist_id)

        if artist is None:
            raise ValueError("작가를 찾을 수 없습니다.")

        update_data = dict(artist)

        if is_favorite is not None:
            update_data["is_favorite"] = int(bool(is_favorite))

        if is_hidden is not None:
            update_data["is_hidden"] = int(bool(is_hidden))

        if artist_tags is not None:
            update_data["artist_tags"] = artist_tags.strip()

        return self.repo.update_artist(
            artist_id,
            update_data,
        )

    def update_rating(
        self,
        artist_id: int,
        rating: int,
    ):
        if rating < 0 or rating > 10:
            raise ValueError("평점은 0~10 사이여야 합니다.")

        artist = self.repo.get_by_id(artist_id)

        if artist is None:
            raise ValueError("작가를 찾을 수 없습니다.")

        return self.repo.update_rating(
            artist_id,
            rating,
        )

    def bulk_update_rating(
        self,
        artist_ids: list[int],
        rating: int,
    ):
        self._validate_artist_ids(artist_ids)

        if rating < 0 or rating > 10:
            raise ValueError("평점은 0~10 사이여야 합니다.")

        return self.repo.bulk_update_rating(
            artist_ids,
            rating,
        )

    def bulk_update_favorite(
        self,
        artist_ids: list[int],
        is_favorite: bool,
    ):
        self._validate_artist_ids(artist_ids)

        return self.repo.bulk_update_favorite(
            artist_ids,
            is_favorite,
        )

    def bulk_update_hidden(
        self,
        artist_ids: list[int],
        is_hidden: bool,
    ):
        self._validate_artist_ids(artist_ids)

        return self.repo.bulk_update_hidden(
            artist_ids,
            is_hidden,
        )

    def _validate_artist_ids(self, artist_ids: list[int]):
        if not artist_ids:
            raise ValueError("선택된 작가가 없습니다.")

        for artist_id in artist_ids:
            if artist_id is None:
                raise ValueError("잘못된 작가 ID가 포함되어 있습니다.")

            if int(artist_id) <= 0:
                raise ValueError("잘못된 작가 ID가 포함되어 있습니다.")

    def toggle_favorite(self, artist_id: int):
        artist = self.repo.get_by_id(artist_id)

        if artist is None:
            raise ValueError("작가를 찾을 수 없습니다.")

        current_value = bool(artist.get("is_favorite", 0))
        return self.repo.update_favorite(
            artist_id,
            not current_value,
        )

    def toggle_hidden(self, artist_id: int):
        artist = self.repo.get_by_id(artist_id)

        if artist is None:
            raise ValueError("작가를 찾을 수 없습니다.")

        current_value = bool(artist.get("is_hidden", 0))
        return self.repo.update_hidden(
            artist_id,
            not current_value,
        )

    def update_last_viewed(self, artist_id: int):
        return self.repo.update_last_viewed(
            artist_id,
        )

    def delete_artist(self, artist_id: int):
        return self.delete_artists([artist_id])

    def delete_artists(self, artist_ids: list[int]) -> str:
        self._validate_artist_ids(artist_ids)

        backup_path = self.backup_service.export_deleted_artists_backup(
            artist_ids
        )

        self.repo.delete_artists(artist_ids)

        return backup_path

    def restore_deleted_artists_backup(
        self,
        file_path: str,
    ) -> dict:
        return self.backup_service.restore_deleted_artists_backup(
            file_path
        )
