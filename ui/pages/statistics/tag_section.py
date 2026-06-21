import webbrowser
from urllib.parse import quote

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


class StatisticsTagSection(QWidget):
    PIXIV_ARTIST_URL = "https://www.pixiv.net/users/{pixiv_id}"
    PIXIV_TAG_URL = "https://www.pixiv.net/tags/{tag}/artworks"

    def __init__(self):
        super().__init__()

        self._setup_ui()

    def _setup_ui(self):
        self.setObjectName("sectionPanel")
        self.setAttribute(Qt.WA_StyledBackground, True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(12)

        title_label = QLabel("태그 분석")
        title_label.setObjectName("sectionTitle")

        self.summary_label = QLabel("-")
        self.summary_label.setObjectName("sectionSummaryLabel")

        self.tab_widget = QTabWidget()
        self.tab_widget.setObjectName("statisticsTabs")

        self.tag_top_table = self._create_tag_top_table()
        self.artist_top_table = self._create_artist_top_table()

        self.tab_widget.addTab(self.tag_top_table, "태그 사용 TOP")
        self.tab_widget.addTab(self.artist_top_table, "태그 보유 작가 TOP")

        layout.addWidget(title_label)
        layout.addWidget(self.summary_label)
        layout.addWidget(self.tab_widget, 1)

    def _create_tag_top_table(self) -> QTableWidget:
        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(
            [
                "순위",
                "태그",
                "사용 수",
            ]
        )

        self._setup_table_base(table)
        table.cellDoubleClicked.connect(
            self._open_pixiv_tag_from_table
        )

        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Fixed)

        table.setColumnWidth(2, 100)

        return table

    def _create_artist_top_table(self) -> QTableWidget:
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(
            [
                "순위",
                "작가명",
                "Pixiv ID",
                "태그 수",
            ]
        )

        self._setup_table_base(table)
        table.cellDoubleClicked.connect(
            self._open_artist_pixiv_from_table
        )

        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        header.setSectionResizeMode(3, QHeaderView.Fixed)

        table.setColumnWidth(2, 110)
        table.setColumnWidth(3, 100)

        return table

    def _setup_table_base(self, table: QTableWidget):
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        table.verticalHeader().setVisible(False)
        table.setAlternatingRowColors(True)
        table.setSortingEnabled(False)
        table.setMinimumHeight(240)

    def update_tag(self, tag_data: dict):
        total_tag_count = self._to_int(tag_data.get("total_tag_count", 0))
        tagged_artist_count = self._to_int(
            tag_data.get("tagged_artist_count", 0)
        )
        untagged_artist_count = self._to_int(
            tag_data.get("untagged_artist_count", 0)
        )

        self.summary_label.setText(
            "전체 태그 "
            f"{total_tag_count:,}개 / "
            f"태그 보유 {tagged_artist_count:,}명 / "
            f"태그 없음 {untagged_artist_count:,}명"
        )

        self._populate_tag_top_table(
            tag_data.get("tag_top", [])
        )
        self._populate_artist_top_table(
            tag_data.get("tag_artist_top", [])
        )

    def _populate_tag_top_table(self, items: list[dict]):
        self.tag_top_table.setRowCount(0)
        self.tag_top_table.setRowCount(len(items))

        for row_index, item in enumerate(items):
            display_tag = self._get_display_tag(item)
            original_tag = self._get_original_tag(item)

            tag_item = self._create_text_item(display_tag)
            tag_item.setData(Qt.UserRole, original_tag)

            self.tag_top_table.setItem(
                row_index,
                0,
                self._create_center_item(str(row_index + 1)),
            )
            self.tag_top_table.setItem(
                row_index,
                1,
                tag_item,
            )
            self.tag_top_table.setItem(
                row_index,
                2,
                self._create_center_item(
                    self._format_count(item.get("count", 0))
                ),
            )

    def _populate_artist_top_table(self, items: list[dict]):
        self.artist_top_table.setRowCount(0)
        self.artist_top_table.setRowCount(len(items))

        for row_index, item in enumerate(items):
            artist = item.get("artist", {}) or {}

            self.artist_top_table.setItem(
                row_index,
                0,
                self._create_center_item(str(row_index + 1)),
            )
            self.artist_top_table.setItem(
                row_index,
                1,
                self._create_text_item(artist.get("artist_name", "-")),
            )
            self.artist_top_table.setItem(
                row_index,
                2,
                self._create_center_item(artist.get("pixiv_id", "-")),
            )
            self.artist_top_table.setItem(
                row_index,
                3,
                self._create_center_item(
                    self._format_count(item.get("tag_count", 0))
                ),
            )

    def _open_pixiv_tag_from_table(
        self,
        row: int,
        column: int,
    ):
        tag_item = self.tag_top_table.item(row, 1)

        if tag_item is None:
            return

        tag = str(tag_item.data(Qt.UserRole) or "").strip()

        if not tag:
            tag = tag_item.text().strip()

        if not tag or tag == "-":
            return

        webbrowser.open(
            self.PIXIV_TAG_URL.format(
                tag=quote(tag),
            )
        )

    def _open_artist_pixiv_from_table(
        self,
        row: int,
        column: int,
    ):
        pixiv_id_item = self.artist_top_table.item(row, 2)

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

    def _get_display_tag(
        self,
        item: dict,
    ) -> str:
        return str(
            item.get("display_tag")
            or item.get("translated_tag")
            or item.get("tag_ko")
            or item.get("ko")
            or item.get("translated")
            or item.get("tag")
            or item.get("original_tag")
            or "-"
        )

    def _get_original_tag(
        self,
        item: dict,
    ) -> str:
        return str(
            item.get("original_tag")
            or item.get("tag_original")
            or item.get("raw_tag")
            or item.get("tag_en")
            or item.get("en")
            or item.get("source_tag")
            or item.get("tag")
            or item.get("display_tag")
            or "-"
        )

    def _create_text_item(self, text: str) -> QTableWidgetItem:
        item = QTableWidgetItem(str(text or "-"))
        item.setToolTip(str(text or "-"))

        return item

    def _create_center_item(self, text: str) -> QTableWidgetItem:
        item = self._create_text_item(text)
        item.setTextAlignment(Qt.AlignCenter)

        return item

    def _format_count(self, value) -> str:
        return f"{self._to_int(value):,}"

    def _to_int(self, value) -> int:
        try:
            return int(value)
        except (TypeError, ValueError):
            return 0
