class UpdateSelectionActions:
    def __init__(self, page):
        self.page = page

    def select_all(self):
        artist_ids = [
            artist.get("id")
            for artist in self.page.artists
            if artist.get("id") is not None
        ]

        self.page.artist_table.select_artist_ids(artist_ids)
        self.page.update_target_count()

    def clear_selection(self):
        self.page.artist_table.clearSelection()
        self.page.update_target_count()

    def select_unknown(self):
        artist_ids = [
            artist.get("id")
            for artist in self.page.artists
            if artist.get("id") is not None
            and artist.get("update_status") in (
                None,
                "",
                "unknown",
            )
        ]

        self.page.artist_table.select_artist_ids(artist_ids)
        self.page.update_target_count()

    def select_need_update(self):
        artist_ids = [
            artist.get("id")
            for artist in self.page.artists
            if artist.get("id") is not None
            and artist.get("update_status") == "need_update"
        ]

        self.page.artist_table.select_artist_ids(artist_ids)
        self.page.update_target_count()

    def select_failed(self):
        artist_ids = [
            artist_id
            for artist_id in self.page.failed_artist_ids
            if artist_id is not None
        ]

        self.page.artist_table.select_artist_ids(artist_ids)
        self.page.update_target_count()

    def get_selected_artist_ids(self) -> list[int]:
        return self.page.artist_table.get_selected_artist_ids()
