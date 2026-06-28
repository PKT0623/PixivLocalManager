class BookmarkSaveHandlerMixin:
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
                cleaned_bookmark_artworks = (
                    self.matcher.match_bookmark_artworks(
                        bookmark_artworks=cleaned_bookmark_artworks,
                        artist_map=artist_map,
                    )
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
