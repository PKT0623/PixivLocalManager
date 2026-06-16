from typing import Optional

from app.database.artist import ArtistRepository
from .folder_scan_service import FolderScanService
from .rescan_service import ArtistRescanService
from .scan_builder import ArtistScanBuilder
from .scan_compare import ArtistScanCompare


class ArtistScanService:
    def __init__(self):
        self.repo = ArtistRepository()
        self.folder_scanner = FolderScanService()
        self.scan_builder = ArtistScanBuilder()
        self.scan_compare = ArtistScanCompare()
        self.rescan_service = ArtistRescanService()

    def save_scanned_artist(
        self,
        folder_path: str,
        rating: int = 0,
        memo: Optional[str] = None,
    ):
        scan_result = self.folder_scanner.scan_folder(folder_path)

        pixiv_id = str(scan_result.pixiv_id or "").strip()

        if not pixiv_id:
            raise ValueError("Pixiv ID를 찾을 수 없습니다.")

        existing_artist = self.repo.get_by_pixiv_id(pixiv_id)

        if existing_artist is None:
            return self._create_scanned_artist(
                scan_result,
                rating,
                memo,
            )

        return self._update_scanned_artist(
            existing_artist,
            scan_result,
            rating,
            memo,
        )

    def rescan_artist_folder(
        self,
        artist_id: int,
    ):
        return self.rescan_service.rescan_artist_folder(
            artist_id,
        )

    def _create_scanned_artist(
        self,
        scan_result,
        rating: int = 0,
        memo: Optional[str] = None,
    ):
        artist_data = self.scan_builder.build_new_artist_data(
            scan_result,
            rating,
            memo,
        )

        artist_id = self.repo.create_artist(artist_data)
        artist = self.repo.get_by_id(artist_id)

        return {
            "action": "created",
            "artist": artist,
            "scan_result": scan_result,
        }

    def _update_scanned_artist(
        self,
        existing_artist: dict,
        scan_result,
        rating: int = 0,
        memo: Optional[str] = None,
    ):
        update_data = self.scan_builder.build_existing_artist_update_data(
            existing_artist,
            scan_result,
            rating,
            memo,
        )

        if not self.scan_compare.has_scan_changes(
            existing_artist,
            update_data,
        ):
            return {
                "action": "unchanged",
                "artist": existing_artist,
                "scan_result": scan_result,
            }

        self.repo.update_artist(
            existing_artist["id"],
            update_data,
        )

        artist = self.repo.get_by_id(existing_artist["id"])

        return {
            "action": "updated",
            "artist": artist,
            "scan_result": scan_result,
        }
