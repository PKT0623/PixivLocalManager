from datetime import datetime, timedelta
from typing import Optional

from app.database.artist_repository import ArtistRepository
from app.services.folder_scan_service import FolderScanService
from app.services.artwork_status_service import ArtworkStatusService
from app.services.pixiv_update_service import PixivUpdateService
from app.services.settings_service import SettingsService


class ArtistService:
    RECENT_CHECK_SKIP_HOURS = 6
    MAX_BULK_UPDATE_COUNT = 20

    def __init__(self):
        self.repo = ArtistRepository()
        self.folder_scanner = FolderScanService()
        self.status_service = ArtworkStatusService()
        self.pixiv_update_service = PixivUpdateService()
        self.settings_service = SettingsService()

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

    def check_artist_update(
        self,
        artist_id: int,
    ) -> dict:
        artist = self.repo.get_by_id(artist_id)

        if artist is None:
            raise ValueError("작가를 찾을 수 없습니다.")

        pixiv_id = str(artist.get("pixiv_id", "") or "").strip()

        if not pixiv_id:
            raise ValueError("작가의 Pixiv ID가 없습니다.")

        phpsessid = self.settings_service.get_setting(
            "pixiv_phpsessid"
        )

        if not phpsessid:
            raise ValueError("Pixiv PHPSESSID가 설정되어 있지 않습니다.")

        fetch_result = self.pixiv_update_service.fetch_artist_artwork_ids(
            pixiv_id=pixiv_id,
            phpsessid=phpsessid,
        )

        status_result = self.status_service.calculate_status(
            artist.get("local_latest_artwork_ids", ""),
            fetch_result.artwork_ids_text,
        )

        update_data = dict(artist)
        update_data["pixiv_latest_artwork_ids"] = (
            fetch_result.artwork_ids_text
        )
        update_data["update_status"] = status_result.status
        update_data["last_checked_at"] = datetime.now().isoformat()

        self.repo.update_artist(
            artist_id,
            update_data,
        )

        updated_artist = self.repo.get_by_id(artist_id)

        return {
            "action": "checked",
            "artist": updated_artist,
            "status": status_result.status,
            "local_count": status_result.local_count,
            "pixiv_count": status_result.pixiv_count,
            "missing_count": status_result.missing_count,
            "missing_ids": status_result.missing_ids,
        }

    def check_all_artist_updates(
        self,
        max_count: int = MAX_BULK_UPDATE_COUNT,
        skip_recent: bool = True,
    ) -> list[dict]:
        artists = self.repo.get_all()
        results = []

        max_count = max(1, min(max_count, self.MAX_BULK_UPDATE_COUNT))

        checked_count = 0

        for artist in artists:
            if checked_count >= max_count:
                break

            if skip_recent and self._was_recently_checked(artist):
                results.append(
                    {
                        "action": "skipped_recent",
                        "artist": artist,
                        "status": artist.get("update_status", "unknown"),
                    }
                )
                continue

            try:
                result = self.check_artist_update(
                    artist["id"]
                )
                results.append(result)
                checked_count += 1
            except RuntimeError as error:
                error_message = str(error)

                self._mark_artist_update_error(
                    artist,
                    error_message,
                )

                results.append(
                    {
                        "action": "error",
                        "artist": artist,
                        "status": "error",
                        "error": error_message,
                    }
                )

                if "HTTP 403" in error_message or "HTTP 429" in error_message:
                    break
            except Exception as error:
                error_message = str(error)

                self._mark_artist_update_error(
                    artist,
                    error_message,
                )

                results.append(
                    {
                        "action": "error",
                        "artist": artist,
                        "status": "error",
                        "error": error_message,
                    }
                )

        return results

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
            "memo": memo or "",
            "folder_size_bytes": scan_result.folder_size_bytes,
            "folder_file_count": scan_result.folder_file_count,
            "folder_artwork_count": scan_result.folder_artwork_count,
            "local_latest_artwork_ids": scan_result.local_latest_artwork_ids,
            "pixiv_latest_artwork_ids": "",
            "update_status": status_result.status,
            "last_checked_at": None,
        }

        artist_id = self.repo.create_artist(artist_data)
        artist = self.repo.get_by_id(artist_id)

        return {
            "action": "created",
            "artist": artist,
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

        if rating:
            update_data["rating"] = rating

        if memo is not None:
            update_data["memo"] = memo

        self.repo.update_artist(
            existing_artist["id"],
            update_data,
        )

        artist = self.repo.get_by_id(existing_artist["id"])

        return {
            "action": "updated",
            "artist": artist,
        }

    def _was_recently_checked(
        self,
        artist: dict,
    ) -> bool:
        last_checked_at = artist.get("last_checked_at")

        if not last_checked_at:
            return False

        try:
            checked_at = datetime.fromisoformat(last_checked_at)
        except ValueError:
            return False

        return datetime.now() - checked_at < timedelta(
            hours=self.RECENT_CHECK_SKIP_HOURS
        )

    def _mark_artist_update_error(
        self,
        artist: dict,
        error_message: str,
    ):
        update_data = dict(artist)
        update_data["update_status"] = "error"
        update_data["last_checked_at"] = datetime.now().isoformat()

        self.repo.update_artist(
            artist["id"],
            update_data,
        )
