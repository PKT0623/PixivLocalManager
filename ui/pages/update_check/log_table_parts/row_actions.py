from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QAbstractItemView,
    QTableWidgetItem,
)

from .constants import RESULT_COLORS


class UpdateLogTableRowActionsMixin:
    def add_log_row(
        self,
        row_data: dict,
    ):
        normalized_row = dict(row_data)
        normalized_row["missing_ids"] = self._normalize_id_list(
            normalized_row.get("missing_ids", [])
        )
        normalized_row["download_candidate_ids"] = self._normalize_id_list(
            normalized_row.get("download_candidate_ids", [])
        )

        self.log_rows.append(normalized_row)
        self.refresh_rows()

    def clear_logs(self):
        self.log_rows = []
        self.setRowCount(0)

    def set_filter(
        self,
        filter_name: str,
    ):
        self.current_filter = filter_name
        self.refresh_rows()

    def refresh_rows(self):
        self.setRowCount(0)

        for row_data in self.log_rows:
            if not self._should_show_row(row_data):
                continue

            self._append_visible_row(row_data)

    def select_log_by_artist_id(
        self,
        artist_id: int,
    ) -> bool:
        for row in range(self.rowCount()):
            item = self.item(row, 0)

            if item is None:
                continue

            row_data = item.data(Qt.UserRole)

            if not isinstance(row_data, dict):
                continue

            if row_data.get("artist_id") != artist_id:
                continue

            self.selectRow(row)
            self.scrollToItem(
                item,
                QAbstractItemView.PositionAtCenter,
            )
            return True

        return False

    def _should_show_row(
        self,
        row_data: dict,
    ) -> bool:
        result = str(row_data.get("result", ""))

        if self.current_filter == "전체":
            return True

        return result == self.current_filter

    def _append_visible_row(
        self,
        row_data: dict,
    ):
        row = self.rowCount()
        self.insertRow(row)

        values = [
            row_data.get("time", "-"),
            row_data.get("progress", "-"),
            row_data.get("result", "-"),
            row_data.get("artist_name", "-"),
            row_data.get("pixiv_id", "-"),
            row_data.get("local_count", "-"),
            row_data.get("pixiv_count", "-"),
            row_data.get("missing_count", "-"),
            self._format_id_list(row_data.get("missing_ids", [])),
            self._format_id_list(row_data.get("download_candidate_ids", [])),
            row_data.get("status", "-"),
        ]

        for column, value in enumerate(values):
            item = QTableWidgetItem(str(value))
            item.setData(Qt.UserRole, row_data)
            self._apply_item_alignment(item, column)
            self._apply_item_color(item, column, values)
            self.setItem(row, column, item)

    def _apply_item_alignment(
        self,
        item: QTableWidgetItem,
        column: int,
    ):
        if column in (0, 1, 2, 4, 5, 6, 7, 10):
            item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        else:
            item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)

    def _apply_item_color(
        self,
        item: QTableWidgetItem,
        column: int,
        values: list,
    ):
        result = values[2]

        if column != 2:
            return

        color = RESULT_COLORS.get(result)

        if color is None:
            return

        item.setForeground(QColor("#ffffff"))
        item.setBackground(QColor(color))
