from datetime import datetime, timedelta

from app.database.artist_repository import ArtistRepository
from app.services.artwork_status_service import ArtworkStatusService
from app.services.pixiv_update_service import PixivUpdateService
from app.services.settings_service import SettingsService


class ArtistUpdateService:
    RECENT_CHECK_SKIP_HOURS = 6
    MAX_BULK_UPDATE_COUNT = 20

    def __init__(self):
        self.repo = ArtistRepository()
        self.status_service = ArtworkStatusService()
        self.pixiv_update_service = PixivUpdateService()
        self.settings_service = SettingsService()

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
