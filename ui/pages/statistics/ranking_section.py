import webbrowser

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from .formatters import format_bytes, format_count


class StatisticsRankingSection(QWidget):
    PIXIV_ARTIST_URL = "https://www.pixiv.net/users/{pixiv_id}"

    RANKING_TABS = {
        "top_artworks": {
            "title": "작품 수 TOP",
            "value_header": "작품 수",
            "value_key": "folder_artwork_count",
            "formatter": "count",
        },
        "top_files": {
            "title": "파일 수 TOP",
            "value_header": "파일 수",
            "value_key": "folder_file_count",
            "formatter": "count",
        },
        "top_storage": {
            "title": "저장 용량 TOP",
            "value_header": "저장 용량",
            "value_key": "folder_size_bytes",
            "formatter": "bytes",
        },
    }

    def __init__(self):
        super().__init__()

        self.tables = {}

        self._setup_ui()

    def _setup_ui(self):
        self.setObjectName("sectionPanel")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setMinimumHeight(420)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(12)

        title_label = QLabel("랭킹")
        title_label.setObjectName("sectionTitle")

        self.tab_widget = QTabWidget()
        self.tab_widget.setObjectName("rankingTabs")

        layout.addWidget(title_label)
        layout.addWidget(self.tab_widget, 1)

        for key, config in self.RANKING_TABS.items():
            table = self._create_table(config["value_header"])
            self.tables[key] = table

            self.tab_widget.addTab(
                table,
                config["title"],
            )

    def _create_table(self, value_header: str) -> QTableWidget:
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(
            [
                "순위",
                "작가명",
                "Pixiv ID",
                value_header,
            ]
        )
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        table.verticalHeader().setVisible(False)
        table.setAlternatingRowColors(True)
        table.setSortingEnabled(False)
        table.setMinimumHeight(340)
        table.cellDoubleClicked.connect(
            lambda row, column, current_table=table: (
                self._open_artist_pixiv_from_table(current_table, row)
            )
        )

        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        header.setSectionResizeMode(3, QHeaderView.Fixed)

        table.setColumnWidth(2, 110)
        table.setColumnWidth(3, 100)

        return table

    def update_ranking(self, ranking_data: dict):
        for key, config in self.RANKING_TABS.items():
            artists = ranking_data.get(key, [])
            table = self.tables.get(key)

            if table is None:
                continue

            self._populate_table(
                table=table,
                artists=artists,
                config=config,
            )

    def _populate_table(
        self,
        table: QTableWidget,
        artists: list[dict],
        config: dict,
    ):
        table.setRowCount(0)
        table.setRowCount(len(artists))

        value_key = config["value_key"]
        formatter = config["formatter"]

        for row_index, artist in enumerate(artists):
            table.setItem(
                row_index,
                0,
                self._create_center_item(str(row_index + 1)),
            )
            table.setItem(
                row_index,
                1,
                self._create_text_item(artist.get("artist_name", "-")),
            )
            table.setItem(
                row_index,
                2,
                self._create_center_item(artist.get("pixiv_id", "-")),
            )
            table.setItem(
                row_index,
                3,
                self._create_center_item(
                    self._format_value(
                        value=artist.get(value_key, 0),
                        formatter=formatter,
                    )
                ),
            )

    def _open_artist_pixiv_from_table(
        self,
        table: QTableWidget,
        row: int,
    ):
        pixiv_id_item = table.item(row, 2)

        if pixiv_id_item is None:
            return

        pixiv_id = pixiv_id_item.text().strip()

        if not pixiv_id or pixiv_id == "-":
            return

        webbrowser.open(
            self.PIXIV_ARTIST_URL.format(
                pixiv_id=pixiv_id,
            )
        )

    def _format_value(self, value, formatter: str) -> str:
        if formatter == "bytes":
            return format_bytes(value)

        return format_count(value)

    def _create_text_item(self, text: str) -> QTableWidgetItem:
        item = QTableWidgetItem(str(text or "-"))
        item.setToolTip(str(text or "-"))

        return item

    def _create_center_item(self, text: str) -> QTableWidgetItem:
        item = self._create_text_item(text)
        item.setTextAlignment(Qt.AlignCenter)

        return item
