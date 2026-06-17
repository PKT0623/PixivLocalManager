from datetime import datetime

from app.database.connection import get_connection


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
        if previous_history is None:
            return {
                "has_previous": False,
                "previous_missing_count": None,
                "missing_delta": 0,
                "new_missing_ids": "",
                "resolved_missing_ids": "",
                "new_missing_count": 0,
                "resolved_missing_count": 0,
            }

        current_missing_count = int(
            current_history.get("missing_count", 0) or 0
        )
        previous_missing_count = int(
            previous_history.get("missing_count", 0) or 0
        )

        current_missing_ids = self._parse_ids(
            current_history.get("missing_ids", "")
        )
        previous_missing_ids = self._parse_ids(
            previous_history.get("missing_ids", "")
        )

        new_missing_ids = [
            artwork_id
            for artwork_id in current_missing_ids
            if artwork_id not in previous_missing_ids
        ]
        resolved_missing_ids = [
            artwork_id
            for artwork_id in previous_missing_ids
            if artwork_id not in current_missing_ids
        ]

        return {
            "has_previous": True,
            "previous_missing_count": previous_missing_count,
            "missing_delta": current_missing_count - previous_missing_count,
            "new_missing_ids": ",".join(new_missing_ids),
            "resolved_missing_ids": ",".join(resolved_missing_ids),
            "new_missing_count": len(new_missing_ids),
            "resolved_missing_count": len(resolved_missing_ids),
        }

    def _parse_ids(
        self,
        value,
    ) -> list[str]:
        if not value:
            return []

        if isinstance(value, list):
            values = value
        else:
            values = str(value).split(",")

        return [
            str(item).strip()
            for item in values
            if str(item).strip()
        ]
