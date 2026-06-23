from datetime import datetime

from app.database.connection import get_connection

from .normalize import normalize_follow_user
from .update_repository import FollowUserUpdateRepository


class FollowUserRepository(FollowUserUpdateRepository):
    def create_follow_user(self, follow_user: dict) -> int:
        data = normalize_follow_user(follow_user)
        now = datetime.now().isoformat()

        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO follow_users (
                    pixiv_user_id,
                    user_name,
                    profile_image_url,
                    comment,
                    artwork_count,
                    file_count,
                    pixiv_tags,
                    local_artist_id,
                    is_local_artist,
                    is_favorite,
                    is_hidden,
                    memo,
                    source_type,
                    last_synced_at,
                    sync_status,
                    sync_error_message,
                    sync_retry_count,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["pixiv_user_id"],
                    data["user_name"],
                    data["profile_image_url"],
                    data["comment"],
                    data["artwork_count"],
                    data["file_count"],
                    data["pixiv_tags"],
                    data["local_artist_id"],
                    data["is_local_artist"],
                    data["is_favorite"],
                    data["is_hidden"],
                    data["memo"],
                    data["source_type"],
                    data["last_synced_at"],
                    data["sync_status"],
                    data["sync_error_message"],
                    data["sync_retry_count"],
                    now,
                    now,
                ),
            )

            conn.commit()

            return cursor.lastrowid

    def upsert_follow_user(self, follow_user: dict) -> int:
        pixiv_user_id = str(follow_user.get("pixiv_user_id", "")).strip()

        if not pixiv_user_id:
            raise ValueError("Pixiv 유저 ID가 비어 있습니다.")

        existing_user = self.get_by_pixiv_user_id(pixiv_user_id)

        if existing_user is None:
            return self.create_follow_user(follow_user)

        update_data = dict(existing_user)
        update_data.update(follow_user)

        self.update_follow_user(
            existing_user["id"],
            update_data,
        )

        return existing_user["id"]

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

    def get_existing_pixiv_user_ids(
        self,
        pixiv_user_ids: list[str],
    ) -> set[str]:
        normalized_ids = self._normalize_unique_ids(pixiv_user_ids)

        if not normalized_ids:
            return set()

        placeholders = ", ".join("?" for _ in normalized_ids)

        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                f"""
                SELECT pixiv_user_id
                FROM follow_users
                WHERE pixiv_user_id IN ({placeholders})
                """,
                tuple(normalized_ids),
            )

            rows = cursor.fetchall()

        return {
            str(row["pixiv_user_id"]).strip()
            for row in rows
            if str(row["pixiv_user_id"]).strip()
        }

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

    def update_follow_user(
        self,
        follow_user_id: int,
        follow_user: dict,
    ) -> None:
        data = normalize_follow_user(follow_user)

        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE follow_users
                SET
                    pixiv_user_id = ?,
                    user_name = ?,
                    profile_image_url = ?,
                    comment = ?,
                    artwork_count = ?,
                    file_count = ?,
                    pixiv_tags = ?,
                    local_artist_id = ?,
                    is_local_artist = ?,
                    is_favorite = ?,
                    is_hidden = ?,
                    memo = ?,
                    source_type = ?,
                    last_synced_at = ?,
                    sync_status = ?,
                    sync_error_message = ?,
                    sync_retry_count = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    data["pixiv_user_id"],
                    data["user_name"],
                    data["profile_image_url"],
                    data["comment"],
                    data["artwork_count"],
                    data["file_count"],
                    data["pixiv_tags"],
                    data["local_artist_id"],
                    data["is_local_artist"],
                    data["is_favorite"],
                    data["is_hidden"],
                    data["memo"],
                    data["source_type"],
                    data["last_synced_at"],
                    data["sync_status"],
                    data["sync_error_message"],
                    data["sync_retry_count"],
                    datetime.now().isoformat(),
                    follow_user_id,
                ),
            )

            conn.commit()

    def delete_follow_user(self, follow_user_id: int) -> None:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                "DELETE FROM follow_users WHERE id = ?",
                (follow_user_id,),
            )

            conn.commit()

    def delete_all(self) -> None:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("DELETE FROM follow_users")
            conn.commit()

    def _normalize_unique_ids(
        self,
        values: list[str],
    ) -> list[str]:
        normalized_values = []

        for value in values:
            normalized_value = str(value or "").strip()

            if not normalized_value:
                continue

            if normalized_value in normalized_values:
                continue

            normalized_values.append(normalized_value)

        return normalized_values
