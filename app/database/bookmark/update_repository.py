from datetime import datetime

from app.database.connection import get_connection


class BookmarkArtworkUpdateRepository:
    def update_sync_result(
        self,
        bookmark_artwork_id: int,
        sync_status: str,
        error_message: str = "",
        retry_count: int = 0,
    ) -> None:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE bookmark_artworks
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
                    bookmark_artwork_id,
                ),
            )

            conn.commit()

    def update_local_match(
        self,
        bookmark_artwork_id: int,
        local_artist_id: int | None,
    ) -> None:
        is_local_artist = 1 if local_artist_id is not None else 0

        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE bookmark_artworks
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
                    bookmark_artwork_id,
                ),
            )

            conn.commit()

    def update_favorite(
        self,
        bookmark_artwork_id: int,
        is_favorite: bool,
    ) -> None:
        self._update_single_field(
            bookmark_artwork_id,
            "is_favorite",
            int(bool(is_favorite)),
        )

    def update_hidden(
        self,
        bookmark_artwork_id: int,
        is_hidden: bool,
    ) -> None:
        self._update_single_field(
            bookmark_artwork_id,
            "is_hidden",
            int(bool(is_hidden)),
        )

    def _update_single_field(
        self,
        bookmark_artwork_id: int,
        field_name: str,
        value,
    ) -> None:
        self._validate_update_field(field_name)

        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                f"""
                UPDATE bookmark_artworks
                SET
                    {field_name} = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    value,
                    datetime.now().isoformat(),
                    bookmark_artwork_id,
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
