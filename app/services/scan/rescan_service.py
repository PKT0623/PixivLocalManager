from app.database.artist import ArtistRepository
from app.services.artwork_status_service import ArtworkStatusService
from .folder_scan_service import FolderScanService


class ArtistRescanService:
    def __init__(self):
        self.repo = ArtistRepository()
        self.folder_scanner = FolderScanService()
        self.status_service = ArtworkStatusService()

    def rescan_artist_folder(
        self,
        artist_id: int,
    ):
        artist = self.repo.get_by_id(artist_id)

        if artist is None:
            raise ValueError("작가를 찾을 수 없습니다.")

        scan_result = self.folder_scanner.scan_folder(
            artist["folder_path"]
        )

        update_data = self._build_rescan_update_data(
            artist,
            scan_result,
        )

        return self.repo.update_artist(
            artist_id,
            update_data,
        )

    def _build_rescan_update_data(
        self,
        artist: dict,
        scan_result,
    ) -> dict:
        status_result = self.status_service.calculate_status(
            scan_result.local_latest_artwork_ids,
            artist.get("pixiv_latest_artwork_ids", ""),
        )

        update_data = dict(artist)
        update_data["folder_size_bytes"] = scan_result.folder_size_bytes
        update_data["folder_file_count"] = scan_result.folder_file_count
        update_data["folder_artwork_count"] = scan_result.folder_artwork_count
        update_data["local_latest_artwork_ids"] = (
            scan_result.local_latest_artwork_ids
        )
        update_data["update_status"] = status_result.status

        return update_data
