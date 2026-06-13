from typing import Optional

from app.database.artist_repository import ArtistRepository
from app.services.folder_scan_service import FolderScanService
from app.services.artwork_status_service import ArtworkStatusService


class ArtistService:
    def __init__(self):
        self.repo = ArtistRepository()
        self.folder_scanner = FolderScanService()
        self.status_service = ArtworkStatusService()

    def create_artist(
        self,
        folder_path: str,
        rating: int = 0,
        memo: Optional[str] = None,
    ):
        scan_result = self.folder_scanner.scan_folder(folder_path)

        status_result = self.status_service.calculate_status(
            scan_result.local_latest_artwork_ids,
            None,
        )

        artist_data = {
            "artist_name": scan_result.artist_name,
            "pixiv_id": scan_result.pixiv_id,
            "folder_path": scan_result.folder_path,
            "rating": rating,
            "status": "active",
            "memo": memo or "",
            "folder_size_bytes": scan_result.folder_size_bytes,
            "folder_file_count": scan_result.folder_file_count,
            "folder_artwork_count": scan_result.folder_artwork_count,
            "local_latest_artwork_ids": scan_result.local_latest_artwork_ids,
            "pixiv_latest_artwork_ids": "",
            "update_status": status_result.status,
            "last_checked_at": None,
        }

        return self.repo.create_artist(artist_data)

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

    def rescan_artist_folder(
        self,
        artist_id: int,
    ):
        artist = self.repo.get_by_id(artist_id)

        scan_result = self.folder_scanner.scan_folder(
            artist["folder_path"]
        )

        status_result = self.status_service.calculate_status(
            scan_result.local_latest_artwork_ids,
            artist.get("pixiv_latest_artwork_ids", ""),
        )

        update_data = {
            "folder_size_bytes": scan_result.folder_size_bytes,
            "folder_file_count": scan_result.folder_file_count,
            "folder_artwork_count": scan_result.folder_artwork_count,
            "local_latest_artwork_ids": (
                scan_result.local_latest_artwork_ids
            ),
            "update_status": status_result.status,
        }

        return self.repo.update_artist(
            artist_id,
            update_data,
        )
