from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QHeaderView,
    QTableWidget,
    QTableWidgetItem,
)

from .utils import format_datetime


class UpdateArtistTable(QTableWidget):
    def __init__(self):
        super().__init__()

        self.artist_checkboxes = {}

        self._setup_ui()

    def _setup_ui(self):
        self.setColumnCount(5)
        self.setHorizontalHeaderLabels(
            [
                "선택",
                "작가명",
                "Pixiv ID",
                "상태",
                "최근 확인",
            ]
        )
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.NoSelection)
        self.verticalHeader().setVisible(False)
        self.setSortingEnabled(False)
        self.setAlternatingRowColors(True)

        header = self.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)

    def load_artists(self, artists: list[dict]):
        self.setRowCount(0)
        self.artist_checkboxes = {}

        for artist in artists:
            row = self.rowCount()
            self.insertRow(row)

            checkbox = QCheckBox()
            checkbox.setChecked(False)

            self.artist_checkboxes[row] = {
                "checkbox": checkbox,
                "artist": artist,
            }

            self.setCellWidget(row, 0, checkbox)
            self._set_table_item(row, 1, artist.get("artist_name", "-"), left=True)
            self._set_table_item(row, 2, artist.get("pixiv_id", "-"))
            self._set_table_item(row, 3, artist.get("update_status", "-"))
            self._set_table_item(
                row,
                4,
                format_datetime(artist.get("last_checked_at")),
            )

    def _set_table_item(
        self,
        row: int,
        column: int,
        value,
        left: bool = False,
    ):
        item = QTableWidgetItem(str(value))

        if left:
            item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        else:
            item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)

        self.setItem(row, column, item)
