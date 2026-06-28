from datetime import datetime

from app.database.connection import get_connection
from app.database.update_history_comparison_repository import (
    build_compared_update_histories,
    build_recent_missing_increased_histories,
    build_update_history_comparison_data,
    collect_artist_ids_from_histories,
)
from app.database.update_history_query_repository import (
    delete_update_histories_by_artist_id,
    get_latest_update_history_by_artist_id,
    get_latest_update_history_per_artist,
    get_recent_error_update_histories,
    get_recent_update_histories,
    get_today_update_histories,
    get_update_histories_by_artist_id,
    get_update_histories_by_artist_ids,
)


class ArtistUpdateHistoryRepository:
    def create_history(
        self,
        history: dict,
    ) -> int:
        with get_connection() as conn:
            cursor = conn.cursor()

            checked_at = history.get("checked_at") or datetime.now().isoformat()

            cursor.execute(
                """
                INSERT INTO artist_update_history (
                    artist_id,
                    artist_name,
                    pixiv_id,
                    checked_at,
                    action,
                    result_status,
                    result_label,
                    local_count,
                    pixiv_count,
                    missing_count,
                    missing_ids,
                    download_candidate_ids,
                    error_message,
                    error_reason
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    history["artist_id"],
                    history.get("artist_name", ""),
                    history.get("pixiv_id", ""),
                    checked_at,
                    history.get("action", "checked"),
                    history.get("result_status", "unknown"),
                    history.get("result_label", ""),
                    int(history.get("local_count", 0) or 0),
                    int(history.get("pixiv_count", 0) or 0),
                    int(history.get("missing_count", 0) or 0),
                    history.get("missing_ids", ""),
                    history.get("download_candidate_ids", ""),
                    history.get("error_message", ""),
                    history.get("error_reason", ""),
                ),
            )

            conn.commit()

            return cursor.lastrowid

    def get_by_artist_id(
        self,
        artist_id: int,
        limit: int = 50,
    ) -> list[dict]:
        return get_update_histories_by_artist_id(
            artist_id=artist_id,
            limit=limit,
        )

    def get_by_artist_ids(
        self,
        artist_ids: list[int],
        limit_per_artist: int = 20,
    ) -> dict[int, list[dict]]:
        return get_update_histories_by_artist_ids(
            artist_ids=artist_ids,
            limit_per_artist=limit_per_artist,
        )

    def get_by_artist_id_with_comparison(
        self,
        artist_id: int,
        limit: int = 50,
    ) -> list[dict]:
        histories = self.get_by_artist_id(
            artist_id=artist_id,
            limit=limit,
        )

        return build_compared_update_histories(histories)

    def get_recent(
        self,
        limit: int = 100,
    ) -> list[dict]:
        return get_recent_update_histories(limit=limit)

    def get_today_histories(self) -> list[dict]:
        return get_today_update_histories()

    def get_recent_error_histories(
        self,
        limit: int = 20,
    ) -> list[dict]:
        return get_recent_error_update_histories(limit=limit)

    def get_latest_history_per_artist(self) -> list[dict]:
        return get_latest_update_history_per_artist()

    def get_latest_by_artist_id(
        self,
        artist_id: int,
    ):
        return get_latest_update_history_by_artist_id(artist_id=artist_id)

    def get_previous_by_artist_id(
        self,
        artist_id: int,
    ):
        rows = self.get_by_artist_id(
            artist_id=artist_id,
            limit=1,
        )

        if not rows:
            return None

        return rows[0]

    def get_recent_missing_increased_artists(
        self,
        limit: int = 20,
    ) -> list[dict]:
        recent_histories = self.get_recent(limit=limit * 3)
        artist_ids = collect_artist_ids_from_histories(recent_histories)

        histories_by_artist_id = self.get_by_artist_ids(
            artist_ids=artist_ids,
            limit_per_artist=2,
        )

        return build_recent_missing_increased_histories(
            recent_histories=recent_histories,
            histories_by_artist_id=histories_by_artist_id,
            limit=limit,
        )

    def delete_by_artist_id(
        self,
        artist_id: int,
    ) -> None:
        delete_update_histories_by_artist_id(artist_id=artist_id)

    def build_comparison(
        self,
        current_history: dict,
        previous_history: dict | None,
    ) -> dict:
        return build_update_history_comparison_data(
            current_history=current_history,
            previous_history=previous_history,
        )
