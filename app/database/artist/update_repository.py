from datetime import datetime

from app.database.connection import get_connection


class ArtistUpdateRepository:

    def update_favorite(
        self,
        artist_id: int,
        is_favorite: bool,
    ) -> None:
        self._update_single_field(
            artist_id,
            "is_favorite",
            int(bool(is_favorite)),
        )

    def update_hidden(
        self,
        artist_id: int,
        is_hidden: bool,
    ) -> None:
        self._update_single_field(
            artist_id,
            "is_hidden",
            int(bool(is_hidden)),
        )

    def update_rating(
        self,
        artist_id: int,
        rating: int,
    ) -> None:
        self._update_single_field(
            artist_id,
            "rating",
            rating,
        )

    def bulk_update_rating(
        self,
        artist_ids: list[int],
        rating: int,
    ) -> None:
        self._bulk_update_field(
            artist_ids,
            "rating",
            rating,
        )

    def bulk_update_favorite(
        self,
        artist_ids: list[int],
        is_favorite: bool,
    ) -> None:
        self._bulk_update_field(
            artist_ids,
            "is_favorite",
            int(bool(is_favorite)),
        )

    def bulk_update_hidden(
        self,
        artist_ids: list[int],
        is_hidden: bool,
    ) -> None:
        self._bulk_update_field(
            artist_ids,
            "is_hidden",
            int(bool(is_hidden)),
        )

    def update_last_viewed(
        self,
        artist_id: int,
    ) -> None:
        now = datetime.now().isoformat()

        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE artists
                SET
                    last_viewed_at = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    now,
                    now,
                    artist_id,
                ),
            )

            conn.commit()

    def _update_single_field(
        self,
        artist_id: int,
        field_name: str,
        value,
    ) -> None:
        self._validate_update_field(field_name)

        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                f"""
                UPDATE artists
                SET
                    {field_name} = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    value,
                    datetime.now().isoformat(),
                    artist_id,
                ),
            )

            conn.commit()

    def _bulk_update_field(
        self,
        artist_ids: list[int],
        field_name: str,
        value,
    ) -> None:
        if not artist_ids:
            return

        self._validate_update_field(field_name)

        placeholders = ",".join(
            "?"
            for _ in artist_ids
        )

        now = datetime.now().isoformat()

        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                f"""
                UPDATE artists
                SET
                    {field_name} = ?,
                    updated_at = ?
                WHERE id IN ({placeholders})
                """,
                (
                    value,
                    now,
                    *artist_ids,
                ),
            )

            conn.commit()

    def _validate_update_field(self, field_name: str) -> None:
        allowed_fields = {
            "rating",
            "is_favorite",
            "is_hidden",
        }

        if field_name not in allowed_fields:
            raise ValueError("허용되지 않은 필드입니다.")
