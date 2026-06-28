from app.database.connection import get_connection

from .helpers import normalize_unique_ids


class BookmarkArtworkQueryRepository:
    def get_by_id(self, bookmark_artwork_id: int):
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                "SELECT * FROM bookmark_artworks WHERE id = ?",
                (bookmark_artwork_id,),
            )

            row = cursor.fetchone()

            if row is None:
                return None

            return dict(row)

    def get_by_artwork_id(self, artwork_id: str):
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT *
                FROM bookmark_artworks
                WHERE artwork_id = ?
                """,
                (artwork_id,),
            )

            row = cursor.fetchone()

            if row is None:
                return None

            return dict(row)

    def get_existing_bookmark_artwork_map(
        self,
        artwork_ids: list[str],
    ) -> dict[str, dict]:
        normalized_ids = self._normalize_unique_ids(artwork_ids)

        if not normalized_ids:
            return {}

        placeholders = ", ".join("?" for _ in normalized_ids)

        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                f"""
                SELECT *
                FROM bookmark_artworks
                WHERE artwork_id IN ({placeholders})
                """,
                tuple(normalized_ids),
            )

            rows = cursor.fetchall()

        return {
            str(row["artwork_id"]).strip(): dict(row)
            for row in rows
            if str(row["artwork_id"]).strip()
        }

    def get_existing_artwork_ids(
        self,
        artwork_ids: list[str],
    ) -> set[str]:
        return set(
            self.get_existing_bookmark_artwork_map(artwork_ids).keys()
        )

    def get_by_artist_id(self, artist_id: str) -> list[dict]:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT *
                FROM bookmark_artworks
                WHERE artist_id = ?
                ORDER BY artwork_id DESC
                """,
                (artist_id,),
            )

            rows = cursor.fetchall()

            return [dict(row) for row in rows]

    def get_all(self) -> list[dict]:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT *
                FROM bookmark_artworks
                ORDER BY artwork_id DESC
                """
            )

            rows = cursor.fetchall()

            return [dict(row) for row in rows]

    def get_count(self) -> int:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM bookmark_artworks")

            return int(cursor.fetchone()[0] or 0)

    def get_unmatched(self) -> list[dict]:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT *
                FROM bookmark_artworks
                WHERE is_local_artist = 0
                   OR local_artist_id IS NULL
                ORDER BY artwork_id DESC
                """
            )

            rows = cursor.fetchall()

            return [dict(row) for row in rows]

    def _normalize_unique_ids(
        self,
        values: list[str],
    ) -> list[str]:
        return normalize_unique_ids(values)
