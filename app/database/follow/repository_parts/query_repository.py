from app.database.connection import get_connection

from .helpers import normalize_unique_ids


class FollowUserQueryRepository:
    def get_by_id(self, follow_user_id: int):
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                "SELECT * FROM follow_users WHERE id = ?",
                (follow_user_id,),
            )

            row = cursor.fetchone()

            if row is None:
                return None

            return dict(row)

    def get_by_pixiv_user_id(self, pixiv_user_id: str):
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT *
                FROM follow_users
                WHERE pixiv_user_id = ?
                """,
                (pixiv_user_id,),
            )

            row = cursor.fetchone()

            if row is None:
                return None

            return dict(row)

    def get_existing_follow_user_map(
        self,
        pixiv_user_ids: list[str],
    ) -> dict[str, dict]:
        normalized_ids = self._normalize_unique_ids(pixiv_user_ids)

        if not normalized_ids:
            return {}

        placeholders = ", ".join("?" for _ in normalized_ids)

        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                f"""
                SELECT *
                FROM follow_users
                WHERE pixiv_user_id IN ({placeholders})
                """,
                tuple(normalized_ids),
            )

            rows = cursor.fetchall()

        return {
            str(row["pixiv_user_id"]).strip(): dict(row)
            for row in rows
            if str(row["pixiv_user_id"]).strip()
        }

    def get_existing_pixiv_user_ids(
        self,
        pixiv_user_ids: list[str],
    ) -> set[str]:
        return set(
            self.get_existing_follow_user_map(pixiv_user_ids).keys()
        )

    def get_all(self) -> list[dict]:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT *
                FROM follow_users
                ORDER BY user_name, pixiv_user_id
                """
            )

            rows = cursor.fetchall()

            return [dict(row) for row in rows]

    def get_count(self) -> int:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM follow_users")

            return int(cursor.fetchone()[0] or 0)

    def get_unmatched(self) -> list[dict]:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT *
                FROM follow_users
                WHERE is_local_artist = 0
                   OR local_artist_id IS NULL
                ORDER BY user_name, pixiv_user_id
                """
            )

            rows = cursor.fetchall()

            return [dict(row) for row in rows]

    def _normalize_unique_ids(
        self,
        values: list[str],
    ) -> list[str]:
        return normalize_unique_ids(values)
