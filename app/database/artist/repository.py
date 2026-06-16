from datetime import datetime

from .columns import ARTIST_COLUMNS
from .restore_repository import ArtistRestoreRepository
from .update_repository import ArtistUpdateRepository
from app.database.connection import get_connection


class ArtistRepository(
    ArtistUpdateRepository,
    ArtistRestoreRepository,
):

    ARTIST_COLUMNS = ARTIST_COLUMNS

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
                    reference_links,
                    download_note,
                    local_latest_artwork_ids,
                    pixiv_latest_artwork_ids,
                    update_status,
                    last_checked_at,
                    last_viewed_at,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                    artist.get("memo", ""),
                    artist.get("reference_links", ""),
                    artist.get("download_note", ""),
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

    def get_by_ids(self, artist_ids: list[int]) -> list[dict]:
        if not artist_ids:
            return []

        placeholders = ",".join(
            "?"
            for _ in artist_ids
        )

        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                f"""
                SELECT *
                FROM artists
                WHERE id IN ({placeholders})
                ORDER BY artist_name
                """,
                tuple(artist_ids),
            )

            rows = cursor.fetchall()

            return [dict(row) for row in rows]

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
                    reference_links = ?,
                    download_note = ?,
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
                    artist.get("memo", ""),
                    artist.get("reference_links", ""),
                    artist.get("download_note", ""),
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

    def delete_artist(self, artist_id: int) -> None:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                "DELETE FROM artists WHERE id = ?",
                (artist_id,),
            )

            conn.commit()

    def delete_artists(self, artist_ids: list[int]) -> None:
        if not artist_ids:
            return

        placeholders = ",".join(
            "?"
            for _ in artist_ids
        )

        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                f"""
                DELETE FROM artists
                WHERE id IN ({placeholders})
                """,
                tuple(artist_ids),
            )

            conn.commit()
