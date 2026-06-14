class UpdateSelectionActions:
    def __init__(self, dialog):
        self.dialog = dialog

    def select_all(self):
        for item in self.dialog.artist_table.artist_checkboxes.values():
            item["checkbox"].setChecked(True)

    def clear_selection(self):
        for item in self.dialog.artist_table.artist_checkboxes.values():
            item["checkbox"].setChecked(False)

    def select_unknown(self):
        for item in self.dialog.artist_table.artist_checkboxes.values():
            artist = item["artist"]
            status = str(artist.get("update_status", ""))

            item["checkbox"].setChecked(status == "unknown")

    def select_need_update(self):
        for item in self.dialog.artist_table.artist_checkboxes.values():
            artist = item["artist"]
            status = str(artist.get("update_status", ""))

            item["checkbox"].setChecked(status == "need_update")

    def get_selected_artist_ids(self) -> list[int]:
        artist_ids = []

        for item in self.dialog.artist_table.artist_checkboxes.values():
            if not item["checkbox"].isChecked():
                continue

            artist = item["artist"]
            artist_id = artist.get("id")

            if artist_id is None:
                continue

            artist_ids.append(int(artist_id))

        return artist_ids
