from typing import Optional

from app.database.artist_repository import ArtistRepository
from app.services.artist_scan_service import ArtistScanService
from app.services.artist_update_service import ArtistUpdateService


class ArtistService:
    def __init__(self):
        self.repo = ArtistRepository()
        self.scan_service = ArtistScanService()
        self.update_service = ArtistUpdateService()

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
        return self.repo.delete_artist(artist_id)
