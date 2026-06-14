from datetime import datetime

from app.database.connection import get_connection


class ArtistRepository:

    def create_artist(self, artist: dict) -> int:
        with get_connection() as conn:
            cursor = conn.cursor()

            now = datetime.now().isoformat()

            cursor.execute(
                """
                INSERT INTO artists (
                    artist_name,
                    pixiv_id,
                    folder_path,
                    folder_size_bytes,
                    folder_file_count,
                    folder_artwork_count,
                    rating,
                    status,
                    is_favorite,
                    is_hidden,
                    artist_tags,
                    memo,
                    local_latest_artwork_ids,
                    pixiv_latest_artwork_ids,
                    update_status,
                    last_checked_at,
                    last_viewed_at,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    artist["artist_name"],
                    artist["pixiv_id"],
                    artist["folder_path"],
                    artist["folder_size_bytes"],
                    artist["folder_file_count"],
                    artist["folder_artwork_count"],
                    artist["rating"],
                    artist["status"],
                    int(bool(artist.get("is_favorite", 0))),
                    int(bool(artist.get("is_hidden", 0))),
                    artist.get("artist_tags", ""),
                    artist["memo"],
                    artist["local_latest_artwork_ids"],
                    artist["pixiv_latest_artwork_ids"],
                    artist["update_status"],
                    artist["last_checked_at"],
                    artist.get("last_viewed_at"),
                    now,
                    now,
                ),
            )

            conn.commit()

            return cursor.lastrowid

    def get_by_id(self, artist_id: int):
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                "SELECT * FROM artists WHERE id = ?",
                (artist_id,),
            )

            row = cursor.fetchone()

            if row is None:
                return None

            return dict(row)

    def get_by_pixiv_id(self, pixiv_id: str):
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT *
                FROM artists
                WHERE pixiv_id = ?
                """,
                (pixiv_id,),
            )

            row = cursor.fetchone()

            if row is None:
                return None

            return dict(row)

    def get_all(self) -> list[dict]:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                "SELECT * FROM artists ORDER BY artist_name"
            )

            rows = cursor.fetchall()

            return [dict(row) for row in rows]

    def update_artist(self, artist_id: int, artist: dict) -> None:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE artists
                SET
                    artist_name = ?,
                    pixiv_id = ?,
                    folder_path = ?,
                    folder_size_bytes = ?,
                    folder_file_count = ?,
                    folder_artwork_count = ?,
                    rating = ?,
                    status = ?,
                    is_favorite = ?,
                    is_hidden = ?,
                    artist_tags = ?,
                    memo = ?,
                    local_latest_artwork_ids = ?,
                    pixiv_latest_artwork_ids = ?,
                    update_status = ?,
                    last_checked_at = ?,
                    last_viewed_at = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    artist["artist_name"],
                    artist["pixiv_id"],
                    artist["folder_path"],
                    artist["folder_size_bytes"],
                    artist["folder_file_count"],
                    artist["folder_artwork_count"],
                    artist["rating"],
                    artist["status"],
                    int(bool(artist.get("is_favorite", 0))),
                    int(bool(artist.get("is_hidden", 0))),
                    artist.get("artist_tags", ""),
                    artist["memo"],
                    artist["local_latest_artwork_ids"],
                    artist["pixiv_latest_artwork_ids"],
                    artist["update_status"],
                    artist["last_checked_at"],
                    artist.get("last_viewed_at"),
                    datetime.now().isoformat(),
                    artist_id,
                ),
            )

            conn.commit()

    def update_favorite(
        self,
        artist_id: int,
        is_favorite: bool,
    ) -> None:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE artists
                SET
                    is_favorite = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    int(bool(is_favorite)),
                    datetime.now().isoformat(),
                    artist_id,
                ),
            )

            conn.commit()

    def update_hidden(
        self,
        artist_id: int,
        is_hidden: bool,
    ) -> None:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE artists
                SET
                    is_hidden = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    int(bool(is_hidden)),
                    datetime.now().isoformat(),
                    artist_id,
                ),
            )

            conn.commit()

    def update_last_viewed(
        self,
        artist_id: int,
    ) -> None:
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
                    datetime.now().isoformat(),
                    datetime.now().isoformat(),
                    artist_id,
                ),
            )

            conn.commit()

    def delete_artist(self, artist_id: int) -> None:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                "DELETE FROM artists WHERE id = ?",
                (artist_id,),
            )

            conn.commit()
