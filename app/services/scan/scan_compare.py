class ArtistScanCompare:

    COMPARE_FIELDS = [
        "artist_name",
        "pixiv_id",
        "folder_path",
        "folder_size_bytes",
        "folder_file_count",
        "folder_artwork_count",
        "local_latest_artwork_ids",
        "update_status",
        "rating",
        "memo",
    ]

    def has_scan_changes(
        self,
        existing_artist: dict,
        update_data: dict,
    ) -> bool:
        for field_name in self.COMPARE_FIELDS:
            old_value = existing_artist.get(field_name)
            new_value = update_data.get(field_name)

            if str(old_value or "") != str(new_value or ""):
                return True

        return False
