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

    def delete_artist(self, artist_id: int):
        return self.repo.delete_artist(artist_id)
