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
                self._build_insert_values(data, now),
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

    def upsert_bookmark_artworks(
        self,
        bookmark_artworks: list[dict],
    ) -> dict:
        saved_count = 0
        updated_count = 0
        skipped_count = 0
        error_count = 0
        errors = []

        if not bookmark_artworks:
            return self._build_batch_result(
                total_count=0,
                saved_count=0,
                updated_count=0,
                skipped_count=0,
                error_count=0,
                errors=[],
            )

        ids = [
            str(bookmark_artwork.get("artwork_id", "") or "").strip()
            for bookmark_artwork in bookmark_artworks
            if str(bookmark_artwork.get("artwork_id", "") or "").strip()
        ]
        existing_map = self.get_existing_bookmark_artwork_map(ids)
        now = datetime.now().isoformat()

        with get_connection() as conn:
            cursor = conn.cursor()

            for bookmark_artwork in bookmark_artworks:
                artwork_id = str(
                    bookmark_artwork.get("artwork_id", "") or ""
                ).strip()

                if not artwork_id:
                    skipped_count += 1
                    continue

                try:
                    data = normalize_bookmark_artwork(bookmark_artwork)

                    existing_artwork = existing_map.get(artwork_id)

                    if existing_artwork is None:
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
                            self._build_insert_values(data, now),
                        )
                        saved_count += 1
                        existing_map[artwork_id] = {
                            "id": cursor.lastrowid,
                            "artwork_id": artwork_id,
                        }
                    else:
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
                            self._build_update_values(
                                data=data,
                                bookmark_artwork_id=existing_artwork["id"],
                                updated_at=now,
                            ),
                        )
                        updated_count += 1
                except Exception as exc:
                    error_count += 1
                    errors.append(
                        {
                            "artwork_id": artwork_id,
                            "error": str(exc),
                        }
                    )

            conn.commit()

        return self._build_batch_result(
            total_count=len(bookmark_artworks),
            saved_count=saved_count,
            updated_count=updated_count,
            skipped_count=skipped_count,
            error_count=error_count,
            errors=errors,
        )

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
                self._build_update_values(
                    data=data,
                    bookmark_artwork_id=bookmark_artwork_id,
                    updated_at=datetime.now().isoformat(),
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

    def _build_insert_values(
        self,
        data: dict,
        now: str,
    ) -> tuple:
        return (
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
        )

    def _build_update_values(
        self,
        data: dict,
        bookmark_artwork_id: int,
        updated_at: str,
    ) -> tuple:
        return (
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
            updated_at,
            bookmark_artwork_id,
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
        return {
            "total_count": total_count,
            "saved_count": saved_count,
            "updated_count": updated_count,
            "skipped_count": skipped_count,
            "error_count": error_count,
            "errors": errors,
        }

    def _normalize_unique_ids(
        self,
        values: list[str],
    ) -> list[str]:
        normalized_values = []

        for value in values:
            normalized_value = str(value or "").strip()

            if not normalized_value:
                continue

            if normalized_value in normalized_values:
                continue

            normalized_values.append(normalized_value)

        return normalized_values
