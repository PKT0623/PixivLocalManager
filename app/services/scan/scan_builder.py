from typing import Optional

from app.services.artwork_status_service import ArtworkStatusService


class ArtistScanBuilder:
    def __init__(self):
        self.status_service = ArtworkStatusService()

    def build_new_artist_data(
        self,
        scan_result,
        rating: int = 0,
        memo: Optional[str] = None,
    ) -> dict:
        status_result = self.status_service.calculate_status(
            scan_result.local_latest_artwork_ids,
            None,
        )

        return {
            "artist_name": scan_result.artist_name,
            "pixiv_id": scan_result.pixiv_id,
            "folder_path": scan_result.folder_path,
            "rating": rating,
            "status": "active",
            "is_favorite": 0,
            "is_hidden": 0,
            "artist_tags": "",
            "memo": memo or "",
            "reference_links": "",
            "download_note": "",
            "folder_size_bytes": scan_result.folder_size_bytes,
            "folder_file_count": scan_result.folder_file_count,
            "folder_artwork_count": scan_result.folder_artwork_count,
            "local_latest_artwork_ids": scan_result.local_latest_artwork_ids,
            "pixiv_latest_artwork_ids": "",
            "update_status": status_result.status,
            "last_checked_at": None,
            "last_viewed_at": None,
        }

    def build_existing_artist_update_data(
        self,
        existing_artist: dict,
        scan_result,
        rating: int = 0,
        memo: Optional[str] = None,
    ) -> dict:
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
        update_data.setdefault("reference_links", "")
        update_data.setdefault("download_note", "")
        update_data.setdefault("last_viewed_at", None)

        if rating:
            update_data["rating"] = rating

        if memo is not None:
            update_data["memo"] = memo

        return update_data
