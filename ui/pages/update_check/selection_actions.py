class UpdateSelectionActions:
    def __init__(self, page):
        self.page = page

    def select_all(self):
        for item in self.page.artist_table.artist_checkboxes.values():
            item["checkbox"].setChecked(True)

        self.page.update_target_count()

    def clear_selection(self):
        for item in self.page.artist_table.artist_checkboxes.values():
            item["checkbox"].setChecked(False)

        self.page.update_target_count()

    def select_unknown(self):
        self._select_by_status("unknown")
        self.page.update_target_count()

    def select_need_update(self):
        self._select_by_status("need_update")
        self.page.update_target_count()

    def select_failed(self):
        failed_ids = set(self.page.failed_artist_ids)

        for item in self.page.artist_table.artist_checkboxes.values():
            artist = item["artist"]
            artist_id = artist.get("id")

            if artist_id is None:
                item["checkbox"].setChecked(False)
                continue

            item["checkbox"].setChecked(int(artist_id) in failed_ids)

        self.page.update_target_count()

    def get_selected_artist_ids(self) -> list[int]:
        artist_ids = []

        for item in self.page.artist_table.artist_checkboxes.values():
            if not item["checkbox"].isChecked():
                continue

            artist = item["artist"]
            artist_id = artist.get("id")

            if artist_id is None:
                continue

            artist_ids.append(int(artist_id))

        return artist_ids

    def _select_by_status(self, status_value: str):
        for item in self.page.artist_table.artist_checkboxes.values():
            artist = item["artist"]
            status = str(artist.get("update_status", ""))

            item["checkbox"].setChecked(status == status_value)
