from ..utils import (
    format_bytes,
    format_datetime_short,
    format_missing_ids,
    format_signed_number,
    to_int,
)


class RecentActivityTableUpdatersMixin:
    def _update_artist_table(
        self,
        key: str,
    ):
        table = self.tables[key]
        artists = self.current_data.get(key, [])
        date_field = table.property("date_field")

        table.setRowCount(max(12, len(artists)))

        for row in range(table.rowCount()):
            if row >= len(artists):
                values = ["-", "-", "-", "-", "-", "-", "-"]
                tooltips = {}
                artist_id = None
            else:
                artist = artists[row]
                artist_name = str(artist.get("artist_name", "") or "-")
                values = [
                    str(row + 1),
                    self._shorten_text(artist_name, limit=18),
                    str(artist.get("pixiv_id", "") or "-"),
                    str(to_int(artist.get("folder_artwork_count", 0))),
                    str(to_int(artist.get("folder_file_count", 0))),
                    format_bytes(artist.get("folder_size_bytes", 0)),
                    format_datetime_short(artist.get(date_field)),
                ]
                tooltips = {1: artist_name}
                artist_id = artist.get("id")

            self._set_row_values(table, row, values, tooltips, artist_id)

    def _update_update_history_table(self):
        key = "recent_update_histories"
        table = self.tables[key]
        histories = self.current_data.get(key, [])

        table.setRowCount(max(12, len(histories)))

        for row in range(table.rowCount()):
            if row >= len(histories):
                values = ["-", "-", "-", "-", "-", "-"]
                tooltips = {}
                artist_id = None
            else:
                history = histories[row]
                artist_name = str(history.get("artist_name", "") or "-")
                values = [
                    str(row + 1),
                    self._shorten_text(artist_name, limit=18),
                    str(history.get("pixiv_id", "") or "-"),
                    str(history.get("result_label", "") or "-"),
                    str(to_int(history.get("missing_count", 0))),
                    format_datetime_short(history.get("checked_at")),
                ]
                tooltips = {1: artist_name}
                artist_id = history.get("artist_id")

            self._set_row_values(table, row, values, tooltips, artist_id)

    def _update_error_history_table(self):
        key = "recent_error_histories"
        table = self.tables[key]
        histories = self.current_data.get(key, [])

        table.setRowCount(max(12, len(histories)))

        for row in range(table.rowCount()):
            if row >= len(histories):
                values = ["-", "-", "-", "-", "-", "-"]
                tooltips = {}
                artist_id = None
            else:
                history = histories[row]
                artist_name = str(history.get("artist_name", "") or "-")
                error_reason = str(history.get("error_reason", "") or "-")
                values = [
                    str(row + 1),
                    self._shorten_text(artist_name, limit=18),
                    str(history.get("pixiv_id", "") or "-"),
                    str(history.get("result_label", "") or "확인 실패"),
                    self._shorten_text(error_reason, limit=16),
                    format_datetime_short(history.get("checked_at")),
                ]
                tooltips = {
                    1: artist_name,
                    4: error_reason,
                }
                artist_id = history.get("artist_id")

            self._set_row_values(table, row, values, tooltips, artist_id)

    def _update_missing_increased_table(self):
        key = "missing_increased_histories"
        table = self.tables[key]
        histories = self.current_data.get(key, [])

        table.setRowCount(max(12, len(histories)))

        for row in range(table.rowCount()):
            if row >= len(histories):
                values = ["-", "-", "-", "-", "-", "-"]
                tooltips = {}
                artist_id = None
            else:
                history = histories[row]
                artist_name = str(history.get("artist_name", "") or "-")
                missing_ids = format_missing_ids(
                    history.get("new_missing_ids", "")
                )
                values = [
                    str(row + 1),
                    self._shorten_text(artist_name, limit=18),
                    str(history.get("pixiv_id", "") or "-"),
                    str(to_int(history.get("missing_count", 0))),
                    format_signed_number(history.get("missing_delta", 0)),
                    missing_ids,
                ]
                tooltips = {
                    1: artist_name,
                    5: missing_ids,
                }
                artist_id = history.get("artist_id")

            self._set_row_values(table, row, values, tooltips, artist_id)
