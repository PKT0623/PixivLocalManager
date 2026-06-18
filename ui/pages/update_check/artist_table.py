from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QTableWidget,
    QTableWidgetItem,
)

from .utils import format_datetime


class UpdateArtistTable(QTableWidget):
    selection_changed = Signal()

    def __init__(self):
        super().__init__()

        self.artists = []

        self._setup_ui()

    def _setup_ui(self):
        self.setColumnCount(4)
        self.setHorizontalHeaderLabels(
            [
                "작가명",
                "Pixiv ID",
                "상태",
                "최근 확인",
            ]
        )
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.verticalHeader().setVisible(False)
        self.setSortingEnabled(False)
        self.setAlternatingRowColors(True)

        header = self.horizontalHeader()
        header.setStretchLastSection(False)

        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        header.setSectionResizeMode(3, QHeaderView.Fixed)

        self.setColumnWidth(1, 100)
        self.setColumnWidth(2, 120)
        self.setColumnWidth(3, 140)

        self.itemSelectionChanged.connect(
            self.selection_changed.emit
        )

    def load_artists(self, artists: list[dict]):
        self.setRowCount(0)
        self.artists = artists

        for artist in artists:
            self._add_artist_row(artist)

        self.clearSelection()
        self.selection_changed.emit()

    def _add_artist_row(self, artist: dict):
        row = self.rowCount()
        self.insertRow(row)

        self._set_table_item(row, 0, artist.get("artist_name", "-"), True)
        self._set_table_item(row, 1, artist.get("pixiv_id", "-"))
        self._set_table_item(row, 2, artist.get("update_status", "-"))
        self._set_table_item(
            row,
            3,
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
        item.setData(
            Qt.UserRole,
            self.artists[row].get("id"),
        )

        if left:
            item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        else:
            item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)

        self.setItem(row, column, item)

    def get_selected_artist_ids(self) -> list[int]:
        selected_rows = {
            index.row()
            for index in self.selectionModel().selectedRows()
        }

        artist_ids = []

        for row in sorted(selected_rows):
            if row < 0 or row >= len(self.artists):
                continue

            artist_id = self.artists[row].get("id")

            if artist_id is None:
                continue

            artist_ids.append(int(artist_id))

        return artist_ids

    def select_artist_ids(
        self,
        artist_ids: list[int],
    ):
        target_ids = {
            int(artist_id)
            for artist_id in artist_ids
        }

        self.clearSelection()
        selection_model = self.selectionModel()

        for row, artist in enumerate(self.artists):
            artist_id = artist.get("id")

            if artist_id is None:
                continue

            if int(artist_id) not in target_ids:
                continue

            index = self.model().index(row, 0)

            selection_model.select(
                index,
                selection_model.SelectionFlag.Select
                | selection_model.SelectionFlag.Rows,
            )

        self.selection_changed.emit()
