from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QHBoxLayout,
    QHeaderView,
    QTableWidget,
    QTableWidgetItem,
    QWidget,
)

from .utils import format_datetime


class UpdateArtistTable(QTableWidget):
    selection_changed = Signal()

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

        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        header.setSectionResizeMode(3, QHeaderView.Fixed)
        header.setSectionResizeMode(4, QHeaderView.Fixed)

        self.setColumnWidth(0, 60)
        self.setColumnWidth(2, 100)
        self.setColumnWidth(3, 120)
        self.setColumnWidth(4, 140)

    def load_artists(self, artists: list[dict]):
        self.setRowCount(0)
        self.artist_checkboxes = {}

        for artist in artists:
            self._add_artist_row(artist)

        self.selection_changed.emit()

    def _add_artist_row(self, artist: dict):
        row = self.rowCount()
        self.insertRow(row)

        checkbox = QCheckBox()
        checkbox.setChecked(False)
        checkbox.stateChanged.connect(
            lambda state, cb=checkbox: self.selection_changed.emit()
        )

        checkbox_widget = QWidget()
        checkbox_layout = QHBoxLayout(checkbox_widget)
        checkbox_layout.setContentsMargins(0, 0, 0, 0)
        checkbox_layout.setAlignment(Qt.AlignCenter)
        checkbox_layout.addWidget(checkbox)

        self.artist_checkboxes[row] = {
            "checkbox": checkbox,
            "artist": artist,
        }

        self.setCellWidget(row, 0, checkbox_widget)
        self._set_table_item(row, 1, artist.get("artist_name", "-"), True)
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
