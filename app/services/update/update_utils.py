from datetime import datetime, timedelta

from app.database.artist import ArtistRepository


class ArtistUpdateUtils:
    RECENT_CHECK_SKIP_HOURS = 6

    def __init__(self):
        self.repo = ArtistRepository()

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
    ):
        update_data = dict(artist)
        update_data["update_status"] = "error"
        update_data["last_checked_at"] = datetime.now().isoformat()

        self.repo.update_artist(
            artist["id"],
            update_data,
        )
