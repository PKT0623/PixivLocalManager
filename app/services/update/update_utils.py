from datetime import datetime, timedelta

from app.database import ArtistUpdateHistoryRepository
from app.database.artist import ArtistRepository


class ArtistUpdateUtils:
    RECENT_CHECK_SKIP_HOURS = 24

    def __init__(self):
        self.repo = ArtistRepository()
        self.history_repo = ArtistUpdateHistoryRepository()

    def was_recently_checked(
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

    def mark_artist_update_error(
        self,
        artist: dict,
        error_message: str,
        error_reason: str = "",
    ):
        checked_at = datetime.now().isoformat()

        update_data = dict(artist)
        update_data["update_status"] = "error"
        update_data["last_checked_at"] = checked_at

        self.repo.update_artist(
            artist["id"],
            update_data,
        )

        self.save_update_history(
            artist=artist,
            checked_at=checked_at,
            action="error",
            result_status="error",
            result_label="확인 실패",
            error_message=error_message,
            error_reason=error_reason,
        )

    def save_skipped_recent_history(
        self,
        artist: dict,
    ):
        checked_at = datetime.now().isoformat()

        self.save_update_history(
            artist=artist,
            checked_at=checked_at,
            action="skipped_recent",
            result_status=artist.get("update_status", "unknown"),
            result_label="스킵",
        )

    def save_update_history(
        self,
        artist: dict,
        checked_at: str,
        action: str,
        result_status: str,
        result_label: str,
        local_count: int = 0,
        pixiv_count: int = 0,
        missing_count: int = 0,
        missing_ids: list[str] | None = None,
        download_candidate_ids: list[str] | None = None,
        error_message: str = "",
        error_reason: str = "",
    ) -> int:
        missing_ids_text = self._ids_to_text(missing_ids)
        download_candidate_ids_text = self._ids_to_text(
            download_candidate_ids
        )

        return self.history_repo.create_history(
            {
                "artist_id": artist["id"],
                "artist_name": artist.get("artist_name", ""),
                "pixiv_id": artist.get("pixiv_id", ""),
                "checked_at": checked_at,
                "action": action,
                "result_status": result_status,
                "result_label": result_label,
                "local_count": local_count,
                "pixiv_count": pixiv_count,
                "missing_count": missing_count,
                "missing_ids": missing_ids_text,
                "download_candidate_ids": download_candidate_ids_text,
                "error_message": error_message,
                "error_reason": error_reason,
            }
        )

    def status_to_label(
        self,
        status: str,
    ) -> str:
        if status == "need_update":
            return "업데이트 필요"

        if status == "up_to_date":
            return "최신"

        if status == "error":
            return "확인 실패"

        if status == "unknown":
            return "미확인"

        return "확인 완료"

    def _ids_to_text(
        self,
        values: list[str] | None,
    ) -> str:
        if not values:
            return ""

        return ",".join(
            str(value).strip()
            for value in values
            if str(value).strip()
        )
