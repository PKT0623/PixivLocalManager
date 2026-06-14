from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from .utils import format_datetime_short, to_int


class RecentArtistsSection(QFrame):
    def __init__(self):
        super().__init__()

        self.recent_artist_limit = 10
        self.recent_artist_limit_buttons = {}
        self.current_artists = []

        self.setObjectName("detailCard")
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(10)

        header_layout = QHBoxLayout()

        title_label = QLabel("최근 등록 작가")
        title_label.setObjectName("sectionTitle")

        button_layout = QHBoxLayout()
        button_layout.setSpacing(6)

        for limit in (10, 20, 50):
            button = QPushButton(str(limit))
            button.setObjectName("limitButton")
            button.clicked.connect(
                lambda checked=False, value=limit: self.set_recent_artist_limit(value)
            )

            self.recent_artist_limit_buttons[limit] = button
            button_layout.addWidget(button)

        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addLayout(button_layout)

        self.recent_artist_table = QTableWidget()
        self.recent_artist_table.setColumnCount(5)
        self.recent_artist_table.setHorizontalHeaderLabels(
            ["No", "작가명", "Pixiv ID", "작품 수", "등록일"]
        )
        self.recent_artist_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.recent_artist_table.setSelectionMode(QAbstractItemView.NoSelection)
        self.recent_artist_table.verticalHeader().setVisible(False)
        self.recent_artist_table.setShowGrid(True)
        self.recent_artist_table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.recent_artist_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        header = self.recent_artist_table.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignCenter)
        header.setSectionResizeMode(0, QHeaderView.Interactive)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Interactive)
        header.setSectionResizeMode(3, QHeaderView.Interactive)
        header.setSectionResizeMode(4, QHeaderView.Interactive)

        self.recent_artist_table.setColumnWidth(0, 50)
        self.recent_artist_table.setColumnWidth(2, 120)
        self.recent_artist_table.setColumnWidth(3, 80)
        self.recent_artist_table.setColumnWidth(4, 150)
        self.recent_artist_table.verticalHeader().setDefaultSectionSize(30)
        self.recent_artist_table.setMinimumHeight(260)

        layout.addLayout(header_layout)
        layout.addWidget(self.recent_artist_table, 1)

        self._update_recent_artist_limit_buttons()

    def set_recent_artist_limit(self, limit: int):
        self.recent_artist_limit = limit
        self._update_recent_artist_limit_buttons()
        self.update_recent_artists(self.current_artists)

    def _update_recent_artist_limit_buttons(self):
        for limit, button in self.recent_artist_limit_buttons.items():
            is_active = limit == self.recent_artist_limit
            button.setProperty("active", is_active)
            button.style().unpolish(button)
            button.style().polish(button)

    def update_recent_artists(self, artists: list[dict]):
        self.current_artists = artists

        sorted_artists = sorted(
            artists,
            key=lambda artist: str(artist.get("created_at", "") or ""),
            reverse=True,
        )

        recent_artists = sorted_artists[: self.recent_artist_limit]
        self.recent_artist_table.setRowCount(self.recent_artist_limit)

        for row in range(self.recent_artist_limit):
            if row >= len(recent_artists):
                values = ["-", "-", "-", "-", "-"]
            else:
                artist = recent_artists[row]
                values = [
                    str(row + 1),
                    str(artist.get("artist_name", "") or "-"),
                    str(artist.get("pixiv_id", "") or "-"),
                    str(to_int(artist.get("folder_artwork_count", 0))),
                    format_datetime_short(artist.get("created_at")),
                ]

            for column, value in enumerate(values):
                self._set_table_item(row, column, value)

    def _set_table_item(self, row: int, column: int, text: str):
        item = QTableWidgetItem(text)

        if column in (0, 2, 3, 4):
            item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        else:
            item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.recent_artist_table.setItem(row, column, item)
