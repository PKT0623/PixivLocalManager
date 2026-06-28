class BookmarkPreviewBuilderMixin:
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
