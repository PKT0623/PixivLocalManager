from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem

from .utils import format_bytes, format_count, to_int


class TopRankingUtilsMixin:
    def _format_value(
        self,
        artist: dict,
        value_field: str,
    ) -> str:
        value = artist.get(value_field, 0)

        if value_field == "folder_size_bytes":
            return format_bytes(value)

        return format_count(to_int(value))

    def _set_row_values(
        self,
        table: QTableWidget,
        row: int,
        values: list[str],
        tooltips: dict[int, str],
        artist_id=None,
    ):
        for column, value in enumerate(values):
            item = QTableWidgetItem(str(value))

            if column == 1:
                item.setTextAlignment(
                    Qt.AlignLeft | Qt.AlignVCenter
                )
            else:
                item.setTextAlignment(
                    Qt.AlignCenter | Qt.AlignVCenter
                )

            if column in tooltips:
                item.setToolTip(tooltips[column])

            if artist_id is not None:
                item.setData(Qt.UserRole, artist_id)

            table.setItem(row, column, item)

    def _handle_item_double_clicked(
        self,
        item: QTableWidgetItem,
    ):
        if item.column() != 1:
            return

        artist_id = item.data(Qt.UserRole)

        if artist_id is None:
            return

        try:
            artist_id = int(artist_id)
        except (TypeError, ValueError):
            return

        self.artist_detail_requested.emit(artist_id)

    def _shorten_text(
        self,
        text: str,
        limit: int = 16,
    ) -> str:
        if len(text) <= limit:
            return text

        return f"{text[:limit]}..."
