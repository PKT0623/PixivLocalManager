from datetime import datetime

from app.database.connection import get_connection

from .normalize import normalize_bookmark_artwork
from .update_repository import BookmarkArtworkUpdateRepository


class BookmarkArtworkRepository(BookmarkArtworkUpdateRepository):
    def create_bookmark_artwork(self, bookmark_artwork: dict) -> int:
        data = normalize_bookmark_artwork(bookmark_artwork)
        now = datetime.now().isoformat()

        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO bookmark_artworks (
                    artwork_id,
                    title,
                    artist_id,
                    artist_name,
                    bookmark_count,
                    page_count,
                    ai_type,
                    is_ai_generated,
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
                    ?, ?, ?, ?, ?, ?,
                    ?, ?, ?
                )
                """,
                (
                    data["artwork_id"],
                    data["title"],
                    data["artist_id"],
                    data["artist_name"],
                    data["bookmark_count"],
                    data["page_count"],
                    data["ai_type"],
                    data["is_ai_generated"],
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

    def upsert_bookmark_artwork(self, bookmark_artwork: dict) -> int:
        artwork_id = str(bookmark_artwork.get("artwork_id", "")).strip()

        if not artwork_id:
            raise ValueError("작품 ID가 비어 있습니다.")

        existing_artwork = self.get_by_artwork_id(artwork_id)

        if existing_artwork is None:
            return self.create_bookmark_artwork(bookmark_artwork)

        update_data = dict(existing_artwork)
        update_data.update(bookmark_artwork)

        self.update_bookmark_artwork(
            existing_artwork["id"],
            update_data,
        )

        return existing_artwork["id"]

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

    def update_bookmark_artwork(
        self,
        bookmark_artwork_id: int,
        bookmark_artwork: dict,
    ) -> None:
        data = normalize_bookmark_artwork(bookmark_artwork)

        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE bookmark_artworks
                SET
                    artwork_id = ?,
                    title = ?,
                    artist_id = ?,
                    artist_name = ?,
                    bookmark_count = ?,
                    page_count = ?,
                    ai_type = ?,
                    is_ai_generated = ?,
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
                    data["artwork_id"],
                    data["title"],
                    data["artist_id"],
                    data["artist_name"],
                    data["bookmark_count"],
                    data["page_count"],
                    data["ai_type"],
                    data["is_ai_generated"],
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
                    bookmark_artwork_id,
                ),
            )

            conn.commit()

    def delete_bookmark_artwork(self, bookmark_artwork_id: int) -> None:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                "DELETE FROM bookmark_artworks WHERE id = ?",
                (bookmark_artwork_id,),
            )

            conn.commit()

    def delete_all(self) -> None:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("DELETE FROM bookmark_artworks")
            conn.commit()
