from app.database.artist import ArtistRepository
from app.services.artwork_status_service import ArtworkStatusService
from app.services.scan import FolderScanService


class ArtistFolderService:
    def __init__(self):
        self.repo = ArtistRepository()
        self.folder_scanner = FolderScanService()
        self.status_service = ArtworkStatusService()

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
