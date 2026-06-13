from datetime import datetime

from app.database.connection import get_connection
from app.models import Artist


class ArtistRepository:

    def create(self, artist: Artist) -> int:
        with get_connection() as conn:
            cursor = conn.cursor()

            now = datetime.now().isoformat()

            cursor.execute(
                """
                INSERT INTO artists (
                    artist_name,
                    pixiv_id,
                    folder_path,
                    rating,
                    status,
                    memo,
                    local_latest_artwork_id,
                    pixiv_latest_artwork_id,
                    update_status,
                    last_checked_at,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    artist.artist_name,
                    artist.pixiv_id,
                    artist.folder_path,
                    artist.rating,
                    artist.status,
                    artist.memo,
                    artist.local_latest_artwork_id,
                    artist.pixiv_latest_artwork_id,
                    artist.update_status,
                    artist.last_checked_at,
                    now,
                    now,
                ),
            )

            conn.commit()

            return cursor.lastrowid

    def get_by_id(self, artist_id: int) -> Artist | None:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                "SELECT * FROM artists WHERE id = ?",
                (artist_id,),
            )

            row = cursor.fetchone()

            if row is None:
                return None

            return Artist(**dict(row))

    def get_all(self) -> list[Artist]:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                "SELECT * FROM artists ORDER BY artist_name"
            )

            rows = cursor.fetchall()

            return [
                Artist(**dict(row))
                for row in rows
            ]

    def update(self, artist: Artist) -> None:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE artists
                SET
                    artist_name = ?,
                    pixiv_id = ?,
                    folder_path = ?,
                    rating = ?,
                    status = ?,
                    memo = ?,
                    local_latest_artwork_id = ?,
                    pixiv_latest_artwork_id = ?,
                    update_status = ?,
                    last_checked_at = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    artist.artist_name,
                    artist.pixiv_id,
                    artist.folder_path,
                    artist.rating,
                    artist.status,
                    artist.memo,
                    artist.local_latest_artwork_id,
                    artist.pixiv_latest_artwork_id,
                    artist.update_status,
                    artist.last_checked_at,
                    datetime.now().isoformat(),
                    artist.id,
                ),
            )

            conn.commit()

    def delete(self, artist_id: int) -> None:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                "DELETE FROM artists WHERE id = ?",
                (artist_id,),
            )

            conn.commit()
