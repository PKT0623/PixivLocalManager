from datetime import datetime

from app.database.connection import get_connection


class ArtistRepository:

    ARTIST_COLUMNS = [
        "artist_name",
        "pixiv_id",
        "folder_path",
        "folder_size_bytes",
        "folder_file_count",
        "folder_artwork_count",
        "rating",
        "status",
        "is_favorite",
        "is_hidden",
        "artist_tags",
        "memo",
        "local_latest_artwork_ids",
        "pixiv_latest_artwork_ids",
        "update_status",
        "last_checked_at",
        "last_viewed_at",
        "created_at",
        "updated_at",
    ]

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

    def insert_restored_artist(self, artist: dict) -> int:
        restored_artist = self._normalize_artist_for_restore(artist)

        with get_connection() as conn:
            cursor = conn.cursor()

            artist_id = restored_artist.get("id")

            if artist_id is not None and self._is_artist_id_available(
                cursor,
                int(artist_id),
            ):
                cursor.execute(
                    """
                    INSERT INTO artists (
                        id,
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
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        int(artist_id),
                        restored_artist["artist_name"],
                        restored_artist["pixiv_id"],
                        restored_artist["folder_path"],
                        restored_artist["folder_size_bytes"],
                        restored_artist["folder_file_count"],
                        restored_artist["folder_artwork_count"],
                        restored_artist["rating"],
                        restored_artist["status"],
                        int(bool(restored_artist.get("is_favorite", 0))),
                        int(bool(restored_artist.get("is_hidden", 0))),
                        restored_artist.get("artist_tags", ""),
                        restored_artist["memo"],
                        restored_artist["local_latest_artwork_ids"],
                        restored_artist["pixiv_latest_artwork_ids"],
                        restored_artist["update_status"],
                        restored_artist["last_checked_at"],
                        restored_artist.get("last_viewed_at"),
                        restored_artist["created_at"],
                        restored_artist["updated_at"],
                    ),
                )
            else:
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
                        restored_artist["artist_name"],
                        restored_artist["pixiv_id"],
                        restored_artist["folder_path"],
                        restored_artist["folder_size_bytes"],
                        restored_artist["folder_file_count"],
                        restored_artist["folder_artwork_count"],
                        restored_artist["rating"],
                        restored_artist["status"],
                        int(bool(restored_artist.get("is_favorite", 0))),
                        int(bool(restored_artist.get("is_hidden", 0))),
                        restored_artist.get("artist_tags", ""),
                        restored_artist["memo"],
                        restored_artist["local_latest_artwork_ids"],
                        restored_artist["pixiv_latest_artwork_ids"],
                        restored_artist["update_status"],
                        restored_artist["last_checked_at"],
                        restored_artist.get("last_viewed_at"),
                        restored_artist["created_at"],
                        restored_artist["updated_at"],
                    ),
                )

            conn.commit()

            return cursor.lastrowid

    def upsert_artist(self, artist: dict) -> int:
        pixiv_id = str(artist.get("pixiv_id", "")).strip()

        if not pixiv_id:
            raise ValueError("Pixiv ID가 없는 작가 데이터는 복원할 수 없습니다.")

        existing_artist = self.get_by_pixiv_id(pixiv_id)

        if existing_artist is None:
            return self.insert_restored_artist(artist)

        update_data = self._normalize_artist_for_restore(artist)
        update_data["id"] = existing_artist["id"]

        self.update_artist(
            existing_artist["id"],
            update_data,
        )

        return existing_artist["id"]

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

    def update_rating(
        self,
        artist_id: int,
        rating: int,
    ) -> None:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE artists
                SET
                    rating = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    rating,
                    datetime.now().isoformat(),
                    artist_id,
                ),
            )

            conn.commit()

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

    def _bulk_update_field(
        self,
        artist_ids: list[int],
        field_name: str,
        value,
    ) -> None:
        allowed_fields = {
            "rating",
            "is_favorite",
            "is_hidden",
        }

        if field_name not in allowed_fields:
            raise ValueError("허용되지 않은 필드입니다.")

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

    def update_last_viewed(
        self,
        artist_id: int,
    ) -> None:
        with get_connection() as conn:
            cursor = conn.cursor()

            now = datetime.now().isoformat()

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

    def _is_artist_id_available(
        self,
        cursor,
        artist_id: int,
    ) -> bool:
        cursor.execute(
            "SELECT id FROM artists WHERE id = ?",
            (artist_id,),
        )

        return cursor.fetchone() is None

    def _normalize_artist_for_restore(self, artist: dict) -> dict:
        now = datetime.now().isoformat()

        return {
            "id": artist.get("id"),
            "artist_name": str(artist.get("artist_name", "")).strip(),
            "pixiv_id": str(artist.get("pixiv_id", "")).strip(),
            "folder_path": str(artist.get("folder_path", "")).strip(),
            "folder_size_bytes": int(artist.get("folder_size_bytes", 0) or 0),
            "folder_file_count": int(artist.get("folder_file_count", 0) or 0),
            "folder_artwork_count": int(
                artist.get("folder_artwork_count", 0) or 0
            ),
            "rating": int(artist.get("rating", 0) or 0),
            "status": str(artist.get("status", "normal") or "normal"),
            "is_favorite": int(bool(artist.get("is_favorite", 0))),
            "is_hidden": int(bool(artist.get("is_hidden", 0))),
            "artist_tags": str(artist.get("artist_tags", "") or ""),
            "memo": str(artist.get("memo", "") or ""),
            "local_latest_artwork_ids": str(
                artist.get("local_latest_artwork_ids", "") or ""
            ),
            "pixiv_latest_artwork_ids": str(
                artist.get("pixiv_latest_artwork_ids", "") or ""
            ),
            "update_status": str(
                artist.get("update_status", "unknown") or "unknown"
            ),
            "last_checked_at": artist.get("last_checked_at"),
            "last_viewed_at": artist.get("last_viewed_at"),
            "created_at": artist.get("created_at") or now,
            "updated_at": artist.get("updated_at") or now,
        }
