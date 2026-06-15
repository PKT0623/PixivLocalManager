from typing import Optional

from app.database.artist_repository import ArtistRepository
from app.services.artwork_status_service import ArtworkStatusService
from app.services.folder_scan_service import FolderScanService


class ArtistScanService:
    def __init__(self):
        self.repo = ArtistRepository()
        self.folder_scanner = FolderScanService()
        self.status_service = ArtworkStatusService()

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
        artist = self.repo.get_by_id(artist_id)

        if artist is None:
            raise ValueError("작가를 찾을 수 없습니다.")

        scan_result = self.folder_scanner.scan_folder(
            artist["folder_path"]
        )

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

        return self.repo.update_artist(
            artist_id,
            update_data,
        )

    def _create_scanned_artist(
        self,
        scan_result,
        rating: int = 0,
        memo: Optional[str] = None,
    ):
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
            "is_favorite": 0,
            "is_hidden": 0,
            "artist_tags": "",
            "memo": memo or "",
            "folder_size_bytes": scan_result.folder_size_bytes,
            "folder_file_count": scan_result.folder_file_count,
            "folder_artwork_count": scan_result.folder_artwork_count,
            "local_latest_artwork_ids": scan_result.local_latest_artwork_ids,
            "pixiv_latest_artwork_ids": "",
            "update_status": status_result.status,
            "last_checked_at": None,
            "last_viewed_at": None,
        }

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
        status_result = self.status_service.calculate_status(
            scan_result.local_latest_artwork_ids,
            existing_artist.get("pixiv_latest_artwork_ids", ""),
        )

        update_data = dict(existing_artist)
        update_data["artist_name"] = scan_result.artist_name
        update_data["pixiv_id"] = scan_result.pixiv_id
        update_data["folder_path"] = scan_result.folder_path
        update_data["folder_size_bytes"] = scan_result.folder_size_bytes
        update_data["folder_file_count"] = scan_result.folder_file_count
        update_data["folder_artwork_count"] = scan_result.folder_artwork_count
        update_data["local_latest_artwork_ids"] = (
            scan_result.local_latest_artwork_ids
        )
        update_data["update_status"] = status_result.status

        update_data.setdefault("is_favorite", 0)
        update_data.setdefault("is_hidden", 0)
        update_data.setdefault("artist_tags", "")
        update_data.setdefault("last_viewed_at", None)

        if rating:
            update_data["rating"] = rating

        if memo is not None:
            update_data["memo"] = memo

        if not self._has_scan_changes(existing_artist, update_data):
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

    def _has_scan_changes(
        self,
        existing_artist: dict,
        update_data: dict,
    ) -> bool:
        compare_fields = [
            "artist_name",
            "pixiv_id",
            "folder_path",
            "folder_size_bytes",
            "folder_file_count",
            "folder_artwork_count",
            "local_latest_artwork_ids",
            "update_status",
            "rating",
            "memo",
        ]

        for field_name in compare_fields:
            old_value = existing_artist.get(field_name)
            new_value = update_data.get(field_name)

            if str(old_value or "") != str(new_value or ""):
                return True

        return False
