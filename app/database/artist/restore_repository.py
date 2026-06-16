from datetime import datetime

from app.database.connection import get_connection


class ArtistRestoreRepository:

    def insert_restored_artist(self, artist: dict) -> int:
        restored_artist = self._normalize_artist_for_restore(artist)

        with get_connection() as conn:
            cursor = conn.cursor()

            artist_id = restored_artist.get("id")

            if artist_id is not None and self._is_artist_id_available(
                cursor,
                int(artist_id),
            ):
                restored_id = self._insert_restored_artist_with_id(
                    cursor,
                    restored_artist,
                    int(artist_id),
                )
            else:
                restored_id = self._insert_restored_artist_without_id(
                    cursor,
                    restored_artist,
                )

            conn.commit()

            return restored_id

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

    def _insert_restored_artist_with_id(
        self,
        cursor,
        restored_artist: dict,
        artist_id: int,
    ) -> int:
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
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                artist_id,
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
                restored_artist.get("memo", ""),
                restored_artist.get("reference_links", ""),
                restored_artist.get("download_note", ""),
                restored_artist["local_latest_artwork_ids"],
                restored_artist["pixiv_latest_artwork_ids"],
                restored_artist["update_status"],
                restored_artist["last_checked_at"],
                restored_artist.get("last_viewed_at"),
                restored_artist["created_at"],
                restored_artist["updated_at"],
            ),
        )

        return cursor.lastrowid

    def _insert_restored_artist_without_id(
        self,
        cursor,
        restored_artist: dict,
    ) -> int:
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
                restored_artist.get("memo", ""),
                restored_artist.get("reference_links", ""),
                restored_artist.get("download_note", ""),
                restored_artist["local_latest_artwork_ids"],
                restored_artist["pixiv_latest_artwork_ids"],
                restored_artist["update_status"],
                restored_artist["last_checked_at"],
                restored_artist.get("last_viewed_at"),
                restored_artist["created_at"],
                restored_artist["updated_at"],
            ),
        )

        return cursor.lastrowid

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
            "folder_size_bytes": int(
                artist.get("folder_size_bytes", 0) or 0
            ),
            "folder_file_count": int(
                artist.get("folder_file_count", 0) or 0
            ),
            "folder_artwork_count": int(
                artist.get("folder_artwork_count", 0) or 0
            ),
            "rating": int(artist.get("rating", 0) or 0),
            "status": str(artist.get("status", "normal") or "normal"),
            "is_favorite": int(bool(artist.get("is_favorite", 0))),
            "is_hidden": int(bool(artist.get("is_hidden", 0))),
            "artist_tags": str(artist.get("artist_tags", "") or ""),
            "memo": str(artist.get("memo", "") or ""),
            "reference_links": str(
                artist.get("reference_links", "") or ""
            ),
            "download_note": str(artist.get("download_note", "") or ""),
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
