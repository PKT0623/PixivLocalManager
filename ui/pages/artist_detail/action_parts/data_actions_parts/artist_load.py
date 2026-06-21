from ...utils import (
    display_value,
    folder_status_label,
    format_datetime,
    format_file_size,
    status_label,
    to_int,
)


class ArtistLoadActions:
    def set_artist(self, artist_id: int):
        self.page.artist_id = artist_id

        try:
            self.page.artist_service.update_last_viewed(artist_id)
        except Exception:
            pass

        artist = self.page.artist_service.get_artist(artist_id)

        if artist is None:
            self.clear_artist()
            return

        self.page.current_artist = artist
        self.set_artist_data(artist)

    def refresh_artist(self):
        if self.page.artist_id is None:
            self.clear_artist()
            return

        artist = self.page.artist_service.get_artist(self.page.artist_id)

        if artist is None:
            self.clear_artist()
            return

        self.page.current_artist = artist
        self.set_artist_data(artist)

    def set_artist_data(self, artist: dict):
        section = self.page.info_section

        section.artist_name_input.setText(
            display_value(artist.get("artist_name"))
        )
        section.pixiv_id_label.setText(
            display_value(artist.get("pixiv_id"))
        )
        section.artwork_count_input.setText(
            str(to_int(artist.get("folder_artwork_count", 0)))
        )
        section.file_count_input.setText(
            str(to_int(artist.get("folder_file_count", 0)))
        )
        section.folder_size_label.setText(
            format_file_size(artist.get("folder_size_bytes", 0))
        )
        section.rating_input.setText(
            str(to_int(artist.get("rating", 0), minimum=0, maximum=10))
        )
        section.status_label.setText(
            status_label(artist.get("status"))
        )
        section.update_status_label.setText(
            status_label(artist.get("update_status"))
        )

        section.favorite_checkbox.setChecked(
            bool(artist.get("is_favorite", 0))
        )
        section.last_checked_at_label.setText(
            format_datetime(artist.get("last_checked_at"))
        )
        section.last_viewed_at_label.setText(
            format_datetime(artist.get("last_viewed_at"))
        )
        section.created_at_label.setText(
            format_datetime(artist.get("created_at"))
        )
        section.updated_at_label.setText(
            format_datetime(artist.get("updated_at"))
        )

        folder_path = display_value(artist.get("folder_path"))
        section.folder_path_input.setText(folder_path)
        section.folder_status_label.setText(
            folder_status_label(folder_path)
        )

        self.set_tag_table_data(
            artist.get("artist_tags", "")
        )
        self.set_missing_artwork_table_data(artist)
        self.set_recent_local_artwork_table_data(folder_path)
        self.set_update_history_table_data(artist.get("id"))

        section.memo_edit.setPlainText(
            str(artist.get("memo", "") or "")
        )
        section.reference_links_edit.setPlainText(
            str(artist.get("reference_links", "") or "")
        )
        section.download_note_edit.setPlainText(
            str(artist.get("download_note", "") or "")
        )

    def clear_artist(self):
        self.page.artist_id = None
        self.page.current_artist = None

        section = self.page.info_section

        section.artist_name_input.clear()
        section.pixiv_id_label.setText("-")
        section.artwork_count_input.clear()
        section.file_count_input.clear()
        section.rating_input.clear()
        section.folder_size_label.setText("-")
        section.status_label.setText("-")
        section.update_status_label.setText("-")
        section.favorite_checkbox.setChecked(False)
        section.last_checked_at_label.setText("-")
        section.last_viewed_at_label.setText("-")
        section.created_at_label.setText("-")
        section.updated_at_label.setText("-")
        section.folder_status_label.setText("-")
        section.tag_table.setRowCount(0)
        section.missing_artwork_table.setRowCount(0)
        section.recent_local_artwork_table.setRowCount(0)
        section.update_history_table.setRowCount(0)
        section.missing_artwork_count_label.setText("누락 작품 ID 목록")
        section.update_history_label.setText("업데이트 이력")
        section.update_history_summary_label.setText("최근 누락 변화: -")
        section.folder_path_input.clear()
        section.memo_edit.clear()
        section.reference_links_edit.clear()
        section.download_note_edit.clear()
