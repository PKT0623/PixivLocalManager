from datetime import datetime

from app.database.connection import get_connection
from app.database.follow.normalize import normalize_follow_user

from .helpers import (
    build_follow_user_batch_result,
    build_follow_user_insert_values,
    build_follow_user_update_values,
)


class FollowUserMutationRepository:
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
                VALUES (
                    ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?
                )
                """,
                self._build_insert_values(data, now),
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

    def upsert_follow_users(
        self,
        follow_users: list[dict],
    ) -> dict:
        saved_count = 0
        updated_count = 0
        skipped_count = 0
        error_count = 0
        errors = []

        if not follow_users:
            return self._build_batch_result(
                total_count=0,
                saved_count=0,
                updated_count=0,
                skipped_count=0,
                error_count=0,
                errors=[],
            )

        ids = [
            str(follow_user.get("pixiv_user_id", "") or "").strip()
            for follow_user in follow_users
            if str(follow_user.get("pixiv_user_id", "") or "").strip()
        ]
        existing_map = self.get_existing_follow_user_map(ids)
        now = datetime.now().isoformat()

        with get_connection() as conn:
            cursor = conn.cursor()

            for follow_user in follow_users:
                pixiv_user_id = str(
                    follow_user.get("pixiv_user_id", "") or ""
                ).strip()

                if not pixiv_user_id:
                    skipped_count += 1
                    continue

                try:
                    data = normalize_follow_user(follow_user)

                    existing_user = existing_map.get(pixiv_user_id)

                    if existing_user is None:
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
                            VALUES (
                                ?, ?, ?, ?, ?, ?,
                                ?, ?, ?, ?, ?, ?,
                                ?, ?, ?, ?, ?, ?, ?
                            )
                            """,
                            self._build_insert_values(data, now),
                        )
                        saved_count += 1
                        existing_map[pixiv_user_id] = {
                            "id": cursor.lastrowid,
                            "pixiv_user_id": pixiv_user_id,
                        }
                    else:
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
                            self._build_update_values(
                                data=data,
                                follow_user_id=existing_user["id"],
                                updated_at=now,
                            ),
                        )
                        updated_count += 1
                except Exception as exc:
                    error_count += 1
                    errors.append(
                        {
                            "pixiv_user_id": pixiv_user_id,
                            "error": str(exc),
                        }
                    )

            conn.commit()

        return self._build_batch_result(
            total_count=len(follow_users),
            saved_count=saved_count,
            updated_count=updated_count,
            skipped_count=skipped_count,
            error_count=error_count,
            errors=errors,
        )

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
                self._build_update_values(
                    data=data,
                    follow_user_id=follow_user_id,
                    updated_at=datetime.now().isoformat(),
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

    def _build_insert_values(
        self,
        data: dict,
        now: str,
    ) -> tuple:
        return build_follow_user_insert_values(
            data=data,
            now=now,
        )

    def _build_update_values(
        self,
        data: dict,
        follow_user_id: int,
        updated_at: str,
    ) -> tuple:
        return build_follow_user_update_values(
            data=data,
            follow_user_id=follow_user_id,
            updated_at=updated_at,
        )

    def _build_batch_result(
        self,
        total_count: int,
        saved_count: int,
        updated_count: int,
        skipped_count: int,
        error_count: int,
        errors: list[dict],
    ) -> dict:
        return build_follow_user_batch_result(
            total_count=total_count,
            saved_count=saved_count,
            updated_count=updated_count,
            skipped_count=skipped_count,
            error_count=error_count,
            errors=errors,
        )
