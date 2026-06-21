from datetime import datetime

from app.database.connection import get_connection
from app.database.update_history_utils import build_update_history_comparison


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
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT *
                FROM artist_update_history
                WHERE artist_id = ?
                ORDER BY checked_at DESC, id DESC
                LIMIT ?
                """,
                (
                    artist_id,
                    limit,
                ),
            )

            rows = cursor.fetchall()

            return [dict(row) for row in rows]

    def get_by_artist_id_with_comparison(
        self,
        artist_id: int,
        limit: int = 50,
    ) -> list[dict]:
        histories = self.get_by_artist_id(
            artist_id=artist_id,
            limit=limit,
        )

        compared_histories = []

        for index, history in enumerate(histories):
            previous_history = None

            if index + 1 < len(histories):
                previous_history = histories[index + 1]

            compared_history = dict(history)
            compared_history.update(
                self.build_comparison(
                    current_history=history,
                    previous_history=previous_history,
                )
            )

            compared_histories.append(compared_history)

        return compared_histories

    def get_recent(
        self,
        limit: int = 100,
    ) -> list[dict]:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT *
                FROM artist_update_history
                ORDER BY checked_at DESC, id DESC
                LIMIT ?
                """,
                (limit,),
            )

            rows = cursor.fetchall()

            return [dict(row) for row in rows]

    def get_today_histories(self) -> list[dict]:
        today = datetime.now().date().isoformat()

        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT *
                FROM artist_update_history
                WHERE date(checked_at) = ?
                ORDER BY checked_at DESC, id DESC
                """,
                (today,),
            )

            rows = cursor.fetchall()

            return [dict(row) for row in rows]

    def get_recent_error_histories(
        self,
        limit: int = 20,
    ) -> list[dict]:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT *
                FROM artist_update_history
                WHERE result_status = 'error'
                   OR result_label = '확인 실패'
                   OR action = 'error'
                ORDER BY checked_at DESC, id DESC
                LIMIT ?
                """,
                (limit,),
            )

            rows = cursor.fetchall()

            return [dict(row) for row in rows]

    def get_latest_history_per_artist(self) -> list[dict]:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT history.*
                FROM artist_update_history AS history
                INNER JOIN (
                    SELECT artist_id, MAX(checked_at) AS latest_checked_at
                    FROM artist_update_history
                    GROUP BY artist_id
                ) AS latest
                    ON history.artist_id = latest.artist_id
                   AND history.checked_at = latest.latest_checked_at
                ORDER BY history.checked_at DESC, history.id DESC
                """
            )

            rows = cursor.fetchall()

            latest_by_artist = {}

            for row in rows:
                history = dict(row)
                artist_id = history.get("artist_id")

                if artist_id in latest_by_artist:
                    continue

                latest_by_artist[artist_id] = history

            return list(latest_by_artist.values())

    def get_latest_by_artist_id(
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
        artist_ids = []

        for history in recent_histories:
            artist_id = history.get("artist_id")

            if artist_id in artist_ids:
                continue

            artist_ids.append(artist_id)

        increased_histories = []

        for artist_id in artist_ids:
            histories = self.get_by_artist_id_with_comparison(
                artist_id=artist_id,
                limit=2,
            )

            if not histories:
                continue

            latest_history = histories[0]
            missing_delta = int(latest_history.get("missing_delta", 0) or 0)

            if missing_delta <= 0:
                continue

            increased_histories.append(latest_history)

            if len(increased_histories) >= limit:
                break

        return increased_histories

    def delete_by_artist_id(
        self,
        artist_id: int,
    ) -> None:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                DELETE FROM artist_update_history
                WHERE artist_id = ?
                """,
                (artist_id,),
            )

            conn.commit()

    def build_comparison(
        self,
        current_history: dict,
        previous_history: dict | None,
    ) -> dict:
        return build_update_history_comparison(
            current_history=current_history,
            previous_history=previous_history,
        )
