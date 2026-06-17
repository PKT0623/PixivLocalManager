from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from .utils import format_bytes, format_count, to_int


class TopRankingSection(QFrame):
    artist_detail_requested = Signal(int)

    RANKING_ITEMS = [
        ("artwork_top", "작품 수 TOP", "folder_artwork_count"),
        ("file_top", "파일 수 TOP", "folder_file_count"),
        ("folder_size_top", "폴더 용량 TOP", "folder_size_bytes"),
    ]

    RANKING_LIMITS = [10, 30, 50]

    def __init__(self):
        super().__init__()

        self.current_limit = 10
        self.current_data = {}
        self.limit_buttons = {}
        self.ranking_tables = {}

        self.setObjectName("detailCard")
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(10)

        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)

        title_label = QLabel("TOP 랭킹")
        title_label.setObjectName("sectionTitle")

        button_layout = QHBoxLayout()
        button_layout.setSpacing(5)

        for limit in self.RANKING_LIMITS:
            button = QPushButton(str(limit))
            button.setObjectName("limitButton")
            button.clicked.connect(
                lambda checked=False, value=limit: self.set_limit(value)
            )

            self.limit_buttons[limit] = button
            button_layout.addWidget(button)

        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addLayout(button_layout)

        ranking_layout = QGridLayout()
        ranking_layout.setSpacing(10)

        for index, item in enumerate(self.RANKING_ITEMS):
            key, title, value_field = item
            self._add_ranking_card(
                parent_layout=ranking_layout,
                row=0,
                column=index,
                key=key,
                title=title,
                value_field=value_field,
            )

        layout.addLayout(header_layout)
        layout.addLayout(ranking_layout, 1)

        self._update_limit_buttons()

    def _add_ranking_card(
        self,
        parent_layout: QGridLayout,
        row: int,
        column: int,
        key: str,
        title: str,
        value_field: str,
    ):
        card = QFrame()
        card.setObjectName("rankingCard")

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(10, 8, 10, 10)
        card_layout.setSpacing(6)

        title_label = QLabel(title)
        title_label.setObjectName("sectionSubTitle")

        table = QTableWidget()
        table.setProperty("value_field", value_field)
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["순위", "작가명", "값"])
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setSelectionMode(QAbstractItemView.NoSelection)
        table.verticalHeader().setVisible(False)
        table.setAlternatingRowColors(True)
        table.setShowGrid(True)
        table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        table.verticalHeader().setDefaultSectionSize(26)
        table.itemDoubleClicked.connect(self._handle_item_double_clicked)

        header = table.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignCenter)
        header.setSectionResizeMode(0, QHeaderView.Interactive)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Interactive)

        table.setColumnWidth(0, 44)
        table.setColumnWidth(2, 82)

        card_layout.addWidget(title_label)
        card_layout.addWidget(table, 1)

        self.ranking_tables[key] = table
        parent_layout.addWidget(card, row, column)

    def set_limit(self, limit: int):
        self.current_limit = limit
        self._update_limit_buttons()
        self.update_top_rankings(self.current_data)

    def _update_limit_buttons(self):
        for limit, button in self.limit_buttons.items():
            is_active = limit == self.current_limit
            button.setProperty("active", is_active)
            button.style().unpolish(button)
            button.style().polish(button)

    def update_top_rankings(self, data: dict):
        self.current_data = data

        for key, table in self.ranking_tables.items():
            artists = data.get(key, [])[: self.current_limit]
            table.setRowCount(self.current_limit)

            for row in range(self.current_limit):
                if row >= len(artists):
                    values = ["-", "-", "-"]
                    tooltips = {}
                    artist_id = None
                else:
                    artist = artists[row]
                    value_field = table.property("value_field")
                    artist_name = str(artist.get("artist_name", "") or "-")
                    values = [
                        str(row + 1),
                        self._shorten_text(artist_name),
                        self._format_value(
                            artist=artist,
                            value_field=value_field,
                        ),
                    ]
                    tooltips = {1: artist_name}
                    artist_id = artist.get("id")

                self._set_row_values(table, row, values, tooltips, artist_id)

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
                item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            else:
                item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)

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
