from app.database.artist import ArtistRepository
from .update_utils import ArtistUpdateUtils


class ArtistBulkUpdateService:
    MAX_BULK_UPDATE_COUNT = 20

    def __init__(
        self,
        update_service,
    ):
        self.repo = ArtistRepository()
        self.update_service = update_service
        self.update_utils = ArtistUpdateUtils()

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

            if skip_recent and self.update_utils.was_recently_checked(
                artist
            ):
                results.append(
                    {
                        "action": "skipped_recent",
                        "artist": artist,
                        "status": artist.get("update_status", "unknown"),
                    }
                )
                continue

            if self._check_artist_update(
                artist,
                results,
            ):
                checked_count += 1
            else:
                if self._should_stop_bulk_update(results):
                    break

        return results

    def _check_artist_update(
        self,
        artist: dict,
        results: list[dict],
    ) -> bool:
        try:
            result = self.update_service.check_artist_update(
                artist["id"]
            )
            results.append(result)

            return True
        except RuntimeError as error:
            error_message = str(error)

            self.update_utils.mark_artist_update_error(
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

            return False
        except Exception as error:
            error_message = str(error)

            self.update_utils.mark_artist_update_error(
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

            return False

    def _should_stop_bulk_update(
        self,
        results: list[dict],
    ) -> bool:
        if not results:
            return False

        latest_result = results[-1]
        error_message = latest_result.get("error", "")

        return "HTTP 403" in error_message or "HTTP 429" in error_message
