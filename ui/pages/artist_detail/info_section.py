from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QTableWidgetItem, QVBoxLayout

from .info_parts import (
    ArtistArtworkSectionMixin,
    ArtistBasicInfoMixin,
    ArtistMemoSectionMixin,
    ArtistUpdateHistoryMixin,
)


class ArtistInfoSection(
    QFrame,
    ArtistBasicInfoMixin,
    ArtistArtworkSectionMixin,
    ArtistUpdateHistoryMixin,
    ArtistMemoSectionMixin,
):
    def __init__(self):
        super().__init__()

        self.setObjectName("infoFrame")
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        form_frame = self._create_basic_info_frame()
        artwork_layout = self._create_artwork_layout()
        update_history_frame = self._create_update_history_frame()
        memo_frame = self._create_memo_frame()

        layout.addWidget(form_frame)
        layout.addLayout(artwork_layout)
        layout.addWidget(update_history_frame)
        layout.addWidget(memo_frame)

    def add_empty_tag_row(self):
        row = self.tag_table.rowCount()
        self.tag_table.insertRow(row)

        original_item = QTableWidgetItem("")
        original_item.setFlags(
            original_item.flags()
            & ~Qt.ItemIsEditable
        )

        self.tag_table.setItem(row, 0, original_item)
        self.tag_table.setItem(row, 1, QTableWidgetItem(""))
        self.tag_table.setItem(row, 2, QTableWidgetItem("0"))
