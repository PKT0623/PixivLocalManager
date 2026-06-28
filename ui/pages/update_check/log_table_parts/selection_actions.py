from PySide6.QtCore import Qt


class UpdateLogTableSelectionActionsMixin:
    def get_selected_log(self) -> dict | None:
        selected_rows = self.selectionModel().selectedRows()

        if not selected_rows:
            return None

        row = selected_rows[0].row()
        item = self.item(row, 0)

        if item is None:
            return None

        row_data = item.data(Qt.UserRole)

        if not isinstance(row_data, dict):
            return None

        return row_data

    def get_selected_artist_ids(self) -> list[int]:
        artist_ids = []

        for selected_row in self.selectionModel().selectedRows():
            row = selected_row.row()
            row_data = self._get_visible_row_data(row)

            if not row_data:
                continue

            artist_id = self._to_int(row_data.get("artist_id"))

            if artist_id is None:
                continue

            if artist_id in artist_ids:
                continue

            artist_ids.append(artist_id)

        return artist_ids

    def get_missing_artist_ids(self) -> list[int]:
        artist_ids = []

        for row_data in self.log_rows:
            artist_id = self._to_int(row_data.get("artist_id"))

            if artist_id is None:
                continue

            missing_ids = self._normalize_id_list(row_data.get("missing_ids"))

            if not missing_ids:
                continue

            if artist_id in artist_ids:
                continue

            artist_ids.append(artist_id)

        return artist_ids

    def get_error_artist_ids(self) -> list[int]:
        artist_ids = []

        for row_data in self.log_rows:
            artist_id = self._to_int(row_data.get("artist_id"))

            if artist_id is None:
                continue

            result = str(row_data.get("result", "") or "")

            if result != "오류":
                continue

            if artist_id in artist_ids:
                continue

            artist_ids.append(artist_id)

        return artist_ids

    def get_download_candidate_rows(self) -> list[dict]:
        rows = []

        for row_data in self.log_rows:
            download_candidate_ids = self._normalize_id_list(
                row_data.get("download_candidate_ids")
            )

            if not download_candidate_ids:
                continue

            normalized_row = dict(row_data)
            normalized_row["download_candidate_ids"] = download_candidate_ids
            rows.append(normalized_row)

        return rows

    def get_csv_data(self) -> tuple[list[str], list[list[str]]]:
        rows = []

        for row_data in self.log_rows:
            rows.append(
                [
                    str(row_data.get("time", "-")),
                    str(row_data.get("progress", "-")),
                    str(row_data.get("result", "-")),
                    str(row_data.get("artist_name", "-")),
                    str(row_data.get("pixiv_id", "-")),
                    str(row_data.get("local_count", "-")),
                    str(row_data.get("pixiv_count", "-")),
                    str(row_data.get("missing_count", "-")),
                    self._format_id_list(row_data.get("missing_ids", [])),
                    self._format_id_list(
                        row_data.get("download_candidate_ids", [])
                    ),
                    str(row_data.get("status", "-")),
                ]
            )

        return self.HEADERS.copy(), rows

    def _handle_cell_double_clicked(
        self,
        row: int,
        column: int,
    ):
        item = self.item(row, column)

        if item is None:
            return

        row_data = item.data(Qt.UserRole)

        if not isinstance(row_data, dict):
            return

        artist_id = row_data.get("artist_id")

        if artist_id is None:
            return

        self.artist_detail_requested.emit(int(artist_id))

    def _get_visible_row_data(
        self,
        row: int,
    ) -> dict | None:
        if row < 0 or row >= self.rowCount():
            return None

        item = self.item(row, 0)

        if item is None:
            return None

        row_data = item.data(Qt.UserRole)

        if not isinstance(row_data, dict):
            return None

        return row_data
