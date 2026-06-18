from datetime import datetime

from app.database.connection import get_connection


class FollowUserRepository:

    def create_follow_user(self, follow_user: dict) -> int:
        data = self._normalize_follow_user(follow_user)
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
        data = self._normalize_follow_user(follow_user)

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

    def update_sync_result(
        self,
        follow_user_id: int,
        sync_status: str,
        error_message: str = "",
        retry_count: int = 0,
    ) -> None:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE follow_users
                SET
                    sync_status = ?,
                    sync_error_message = ?,
                    sync_retry_count = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    sync_status,
                    error_message,
                    retry_count,
                    datetime.now().isoformat(),
                    follow_user_id,
                ),
            )

            conn.commit()

    def update_local_match(
        self,
        follow_user_id: int,
        local_artist_id: int | None,
    ) -> None:
        is_local_artist = 1 if local_artist_id is not None else 0

        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE follow_users
                SET
                    local_artist_id = ?,
                    is_local_artist = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    local_artist_id,
                    is_local_artist,
                    datetime.now().isoformat(),
                    follow_user_id,
                ),
            )

            conn.commit()

    def update_favorite(
        self,
        follow_user_id: int,
        is_favorite: bool,
    ) -> None:
        self._update_single_field(
            follow_user_id,
            "is_favorite",
            int(bool(is_favorite)),
        )

    def update_hidden(
        self,
        follow_user_id: int,
        is_hidden: bool,
    ) -> None:
        self._update_single_field(
            follow_user_id,
            "is_hidden",
            int(bool(is_hidden)),
        )

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

    def _update_single_field(
        self,
        follow_user_id: int,
        field_name: str,
        value,
    ) -> None:
        self._validate_update_field(field_name)

        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                f"""
                UPDATE follow_users
                SET
                    {field_name} = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    value,
                    datetime.now().isoformat(),
                    follow_user_id,
                ),
            )

            conn.commit()

    def _validate_update_field(self, field_name: str) -> None:
        allowed_fields = {
            "is_favorite",
            "is_hidden",
        }

        if field_name not in allowed_fields:
            raise ValueError("허용되지 않은 필드입니다.")

    def _normalize_follow_user(self, follow_user: dict) -> dict:
        pixiv_user_id = str(
            follow_user.get("pixiv_user_id", "") or ""
        ).strip()

        if not pixiv_user_id:
            raise ValueError("Pixiv 유저 ID가 비어 있습니다.")

        local_artist_id = follow_user.get("local_artist_id")

        if local_artist_id in ("", 0):
            local_artist_id = None

        if local_artist_id is not None:
            local_artist_id = int(local_artist_id)

        is_local_artist = int(
            bool(follow_user.get("is_local_artist", False))
            or local_artist_id is not None
        )

        return {
            "pixiv_user_id": pixiv_user_id,
            "user_name": str(follow_user.get("user_name", "") or "").strip(),
            "profile_image_url": str(
                follow_user.get("profile_image_url", "") or ""
            ).strip(),
            "comment": str(follow_user.get("comment", "") or ""),
            "artwork_count": int(follow_user.get("artwork_count", 0) or 0),
            "file_count": int(follow_user.get("file_count", 0) or 0),
            "pixiv_tags": str(follow_user.get("pixiv_tags", "") or ""),
            "local_artist_id": local_artist_id,
            "is_local_artist": is_local_artist,
            "is_favorite": int(bool(follow_user.get("is_favorite", 0))),
            "is_hidden": int(bool(follow_user.get("is_hidden", 0))),
            "memo": str(follow_user.get("memo", "") or ""),
            "source_type": str(
                follow_user.get("source_type", "manual") or "manual"
            ),
            "last_synced_at": follow_user.get("last_synced_at"),
            "sync_status": str(
                follow_user.get("sync_status", "pending") or "pending"
            ),
            "sync_error_message": str(
                follow_user.get("sync_error_message", "") or ""
            ),
            "sync_retry_count": int(
                follow_user.get("sync_retry_count", 0) or 0
            ),
        }
