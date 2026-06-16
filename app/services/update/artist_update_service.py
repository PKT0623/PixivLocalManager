from datetime import datetime

from app.database.artist import ArtistRepository
from .bulk_update_service import ArtistBulkUpdateService
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
        self.bulk_update_service = ArtistBulkUpdateService(self)

    def check_artist_update(
        self,
        artist_id: int,
    ) -> dict:
        artist = self.repo.get_by_id(artist_id)

        if artist is None:
            raise ValueError("작가를 찾을 수 없습니다.")

        pixiv_id = self._get_artist_pixiv_id(artist)
        phpsessid = self._get_pixiv_phpsessid()

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
        return self.bulk_update_service.check_all_artist_updates(
            max_count=max_count,
            skip_recent=skip_recent,
        )

    def _get_artist_pixiv_id(
        self,
        artist: dict,
    ) -> str:
        pixiv_id = str(artist.get("pixiv_id", "") or "").strip()

        if not pixiv_id:
            raise ValueError("작가의 Pixiv ID가 없습니다.")

        return pixiv_id

    def _get_pixiv_phpsessid(self) -> str:
        phpsessid = self.settings_service.get_setting(
            "pixiv_phpsessid"
        )

        if not phpsessid:
            raise ValueError("Pixiv PHPSESSID가 설정되어 있지 않습니다.")

        return phpsessid
