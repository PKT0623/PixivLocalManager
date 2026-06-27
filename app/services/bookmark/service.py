from app.database import BookmarkArtworkRepository

from .importer import BookmarkArtworkImporter
from .matcher import BookmarkArtworkMatcher


class BookmarkService:
    def __init__(self):
        self.repo = BookmarkArtworkRepository()
        self.matcher = BookmarkArtworkMatcher()
        self.importer = BookmarkArtworkImporter()

    def create_bookmark_artwork(
        self,
        bookmark_artwork: dict,
        match_local_artist: bool = True,
    ) -> int:
        save_data = dict(bookmark_artwork)

        if match_local_artist:
            save_data = self.matcher.match_bookmark_artwork(save_data)

        return self.repo.create_bookmark_artwork(save_data)

    def upsert_bookmark_artwork(
        self,
        bookmark_artwork: dict,
        match_local_artist: bool = True,
    ) -> int:
        save_data = dict(bookmark_artwork)

        if match_local_artist:
            save_data = self.matcher.match_bookmark_artwork(save_data)

        return self.repo.upsert_bookmark_artwork(save_data)

    def save_bookmark_artworks(
        self,
        bookmark_artworks: list[dict],
        match_local_artist: bool = True,
    ) -> dict:
        saved_count = 0
        updated_count = 0
        skipped_count = 0
        error_count = 0
        errors = []

        cleaned_bookmark_artworks = []
        existing_ids = self.repo.get_existing_artwork_ids(
            self._extract_artwork_ids(bookmark_artworks)
        )

        for bookmark_artwork in bookmark_artworks:
            artwork_id = str(
                bookmark_artwork.get("artwork_id", "") or ""
            ).strip()

            if not artwork_id:
                skipped_count += 1
                continue

            item = dict(bookmark_artwork)
            item["artwork_id"] = artwork_id
            cleaned_bookmark_artworks.append(item)

        try:
            if match_local_artist:
                artist_map = self.matcher.get_artist_map()
                cleaned_bookmark_artworks = self.matcher.match_bookmark_artworks(
                    bookmark_artworks=cleaned_bookmark_artworks,
                    artist_map=artist_map,
                )

            save_result = self.repo.upsert_bookmark_artworks(
                cleaned_bookmark_artworks
            )
            saved_count = save_result["saved_count"]
            updated_count = save_result["updated_count"]
            error_count = save_result["error_count"]
            errors = save_result["errors"]
        except Exception as exc:
            error_count += len(cleaned_bookmark_artworks)
            errors.append(
                {
                    "artwork_id": "-",
                    "error": str(exc),
                }
            )

        for bookmark_artwork in cleaned_bookmark_artworks:
            artwork_id = str(
                bookmark_artwork.get("artwork_id", "") or ""
            ).strip()

            if artwork_id and artwork_id not in existing_ids:
                existing_ids.add(artwork_id)

        return {
            "total_count": len(bookmark_artworks),
            "saved_count": saved_count,
            "updated_count": updated_count,
            "skipped_count": skipped_count,
            "error_count": error_count,
            "errors": errors,
        }

    def preview_bookmark_artworks(
        self,
        bookmark_artworks: list[dict],
    ) -> dict:
        return self._build_preview_result(bookmark_artworks)

    def preview_txt_ids(
        self,
        file_path: str,
    ) -> dict:
        bookmark_artworks = self.importer.parse_txt_file(file_path)

        return self.preview_bookmark_artworks(bookmark_artworks)

    def preview_csv_ids(
        self,
        file_path: str,
    ) -> dict:
        bookmark_artworks = self.importer.parse_csv_file(file_path)

        return self.preview_bookmark_artworks(bookmark_artworks)

    def import_txt_ids(
        self,
        file_path: str,
        match_local_artist: bool = True,
    ) -> dict:
        bookmark_artworks = self.importer.parse_txt_file(file_path)

        return self.import_bookmark_artworks(
            bookmark_artworks=bookmark_artworks,
            match_local_artist=match_local_artist,
        )

    def import_csv_ids(
        self,
        file_path: str,
        match_local_artist: bool = True,
    ) -> dict:
        bookmark_artworks = self.importer.parse_csv_file(file_path)

        return self.import_bookmark_artworks(
            bookmark_artworks=bookmark_artworks,
            match_local_artist=match_local_artist,
        )

    def import_bookmark_artworks(
        self,
        bookmark_artworks: list[dict],
        match_local_artist: bool = True,
    ) -> dict:
        preview = self.preview_bookmark_artworks(bookmark_artworks)
        save_result = self.save_bookmark_artworks(
            bookmark_artworks=preview["new_items"],
            match_local_artist=match_local_artist,
        )

        return {
            **preview,
            "save_result": save_result,
        }

    def get_bookmark_artwork(
        self,
        bookmark_artwork_id: int,
    ):
        return self.repo.get_by_id(bookmark_artwork_id)

    def get_bookmark_artwork_by_artwork_id(
        self,
        artwork_id: str,
    ):
        return self.repo.get_by_artwork_id(artwork_id)

    def get_bookmark_artworks_by_artist_id(
        self,
        artist_id: str,
    ) -> list[dict]:
        return self.repo.get_by_artist_id(artist_id)

    def get_all_bookmark_artworks(self) -> list[dict]:
        return self.repo.get_all()

    def get_unmatched_bookmark_artworks(self) -> list[dict]:
        return self.repo.get_unmatched()

    def update_bookmark_artwork(
        self,
        bookmark_artwork_id: int,
        bookmark_artwork: dict,
        match_local_artist: bool = True,
    ) -> None:
        update_data = dict(bookmark_artwork)

        if match_local_artist:
            update_data = self.matcher.match_bookmark_artwork(update_data)

        return self.repo.update_bookmark_artwork(
            bookmark_artwork_id,
            update_data,
        )

    def match_all_bookmark_artworks(self) -> dict:
        return self.matcher.match_all()

    def toggle_favorite(
        self,
        bookmark_artwork_id: int,
    ) -> None:
        bookmark_artwork = self.repo.get_by_id(bookmark_artwork_id)

        if bookmark_artwork is None:
            raise ValueError("북마크 작품을 찾을 수 없습니다.")

        current_value = bool(bookmark_artwork.get("is_favorite", 0))

        return self.repo.update_favorite(
            bookmark_artwork_id,
            not current_value,
        )

    def toggle_hidden(
        self,
        bookmark_artwork_id: int,
    ) -> None:
        bookmark_artwork = self.repo.get_by_id(bookmark_artwork_id)

        if bookmark_artwork is None:
            raise ValueError("북마크 작품을 찾을 수 없습니다.")

        current_value = bool(bookmark_artwork.get("is_hidden", 0))

        return self.repo.update_hidden(
            bookmark_artwork_id,
            not current_value,
        )

    def delete_bookmark_artwork(
        self,
        bookmark_artwork_id: int,
    ) -> None:
        return self.repo.delete_bookmark_artwork(bookmark_artwork_id)

    def delete_all_bookmark_artworks(self) -> None:
        return self.repo.delete_all()

    def _build_preview_result(
        self,
        bookmark_artworks: list[dict],
    ) -> dict:
        seen_ids = set()
        new_items = []
        duplicate_in_file_items = []
        duplicate_existing_items = []
        existing_ids = self.repo.get_existing_artwork_ids(
            self._extract_artwork_ids(bookmark_artworks)
        )

        for bookmark_artwork in bookmark_artworks:
            artwork_id = str(
                bookmark_artwork.get("artwork_id", "") or ""
            ).strip()

            if not artwork_id:
                continue

            item = dict(bookmark_artwork)
            item["artwork_id"] = artwork_id

            if artwork_id in seen_ids:
                duplicate_in_file_items.append(item)
                continue

            seen_ids.add(artwork_id)

            if artwork_id in existing_ids:
                duplicate_existing_items.append(item)
                continue

            new_items.append(item)

        return {
            "total_count": len(bookmark_artworks),
            "new_count": len(new_items),
            "duplicate_in_file_count": len(duplicate_in_file_items),
            "duplicate_existing_count": len(duplicate_existing_items),
            "new_items": new_items,
            "duplicate_in_file_items": duplicate_in_file_items,
            "duplicate_existing_items": duplicate_existing_items,
        }

    def _extract_artwork_ids(
        self,
        bookmark_artworks: list[dict],
    ) -> list[str]:
        return [
            str(bookmark_artwork.get("artwork_id", "") or "").strip()
            for bookmark_artwork in bookmark_artworks
            if str(bookmark_artwork.get("artwork_id", "") or "").strip()
        ]
