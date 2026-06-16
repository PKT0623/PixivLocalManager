from typing import Optional

from app.database.artist import ArtistRepository
from app.services.artist import (
    ArtistDeleteService,
    ArtistFolderService,
    ArtistMetadataService,
)
from app.services.scan import ArtistScanService
from app.services.update import ArtistUpdateService


class ArtistService:
    def __init__(self):
        self.repo = ArtistRepository()
        self.scan_service = ArtistScanService()
        self.update_service = ArtistUpdateService()
        self.metadata_service = ArtistMetadataService()
        self.folder_service = ArtistFolderService()
        self.delete_service = ArtistDeleteService()

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
        return self.folder_service.change_artist_folder(
            artist_id=artist_id,
            folder_path=folder_path,
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
        return self.metadata_service.update_artist_metadata(
            artist_id=artist_id,
            is_favorite=is_favorite,
            is_hidden=is_hidden,
            artist_tags=artist_tags,
        )

    def update_rating(
        self,
        artist_id: int,
        rating: int,
    ):
        return self.metadata_service.update_rating(
            artist_id=artist_id,
            rating=rating,
        )

    def bulk_update_rating(
        self,
        artist_ids: list[int],
        rating: int,
    ):
        return self.metadata_service.bulk_update_rating(
            artist_ids=artist_ids,
            rating=rating,
        )

    def bulk_update_favorite(
        self,
        artist_ids: list[int],
        is_favorite: bool,
    ):
        return self.metadata_service.bulk_update_favorite(
            artist_ids=artist_ids,
            is_favorite=is_favorite,
        )

    def bulk_update_hidden(
        self,
        artist_ids: list[int],
        is_hidden: bool,
    ):
        return self.metadata_service.bulk_update_hidden(
            artist_ids=artist_ids,
            is_hidden=is_hidden,
        )

    def toggle_favorite(self, artist_id: int):
        return self.metadata_service.toggle_favorite(
            artist_id,
        )

    def toggle_hidden(self, artist_id: int):
        return self.metadata_service.toggle_hidden(
            artist_id,
        )

    def update_last_viewed(self, artist_id: int):
        return self.metadata_service.update_last_viewed(
            artist_id,
        )

    def delete_artist(self, artist_id: int):
        return self.delete_service.delete_artist(
            artist_id,
        )

    def delete_artists(self, artist_ids: list[int]) -> str:
        return self.delete_service.delete_artists(
            artist_ids,
        )

    def restore_deleted_artists_backup(
        self,
        file_path: str,
    ) -> dict:
        return self.delete_service.restore_deleted_artists_backup(
            file_path,
        )
