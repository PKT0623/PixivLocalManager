from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from .utils import (
    format_bytes,
    format_datetime_short,
    format_missing_ids,
    format_signed_number,
    to_int,
)


class RecentActivitySection(QFrame):
    artist_detail_requested = Signal(int)

    ACTIVITY_TABS = [
        ("recent_viewed_artists", "최근 열람"),
        ("recent_registered_artists", "최근 등록"),
        ("recent_checked_artists", "최근 확인"),
        ("recent_update_histories", "업데이트 이력"),
        ("recent_error_histories", "오류 작가"),
        ("missing_increased_histories", "누락 증가"),
    ]

    def __init__(self):
        super().__init__()

        self.current_data = {}
        self.tab_buttons = {}
        self.tables = {}

        self.setObjectName("detailCard")
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(8)

        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)

        title_label = QLabel("최근 활동")
        title_label.setObjectName("sectionTitle")

        tab_layout = QHBoxLayout()
        tab_layout.setSpacing(5)

        for index, (key, title) in enumerate(self.ACTIVITY_TABS):
            button = QPushButton(title)
            button.setObjectName("limitButton")
            button.clicked.connect(
                lambda checked=False, value=index: self.set_active_tab(value)
            )

            self.tab_buttons[index] = button
            tab_layout.addWidget(button)

        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addLayout(tab_layout)

        self.stack = QStackedWidget()

        self._add_artist_table(
            key="recent_viewed_artists",
            headers=[
                "No",
                "작가명",
                "Pixiv ID",
                "작품",
                "파일",
                "용량",
                "최근 열람",
            ],
            date_field="last_viewed_at",
        )
        self._add_artist_table(
            key="recent_registered_artists",
            headers=[
                "No",
                "작가명",
                "Pixiv ID",
                "작품",
                "파일",
                "용량",
                "등록일",
            ],
            date_field="created_at",
        )
        self._add_artist_table(
            key="recent_checked_artists",
            headers=[
                "No",
                "작가명",
                "Pixiv ID",
                "작품 수",
                "파일 수",
                "용량",
                "최근 확인",
            ],
            date_field="last_checked_at",
        )
        self._add_history_table(
            key="recent_update_histories",
            headers=[
                "No",
                "작가명",
                "Pixiv ID",
                "결과",
                "누락",
                "확인일",
            ],
        )
        self._add_history_table(
            key="recent_error_histories",
            headers=[
                "No",
                "작가명",
                "Pixiv ID",
                "오류",
                "사유",
                "확인일",
            ],
        )
        self._add_history_table(
            key="missing_increased_histories",
            headers=[
                "No",
                "작가명",
                "Pixiv ID",
                "누락",
                "변화",
                "신규 ID",
            ],
        )

        layout.addLayout(header_layout)
        layout.addWidget(self.stack, 1)

        self.set_active_tab(0)

    def _add_artist_table(
        self,
        key: str,
        headers: list[str],
        date_field: str,
    ):
        table = self._create_table(headers)
        table.setProperty("date_field", date_field)

        self.tables[key] = table
        self.stack.addWidget(table)

    def _add_history_table(
        self,
        key: str,
        headers: list[str],
    ):
        table = self._create_table(headers)

        self.tables[key] = table
        self.stack.addWidget(table)

    def _create_table(
        self,
        headers: list[str],
    ) -> QTableWidget:
        table = QTableWidget()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setSelectionMode(QAbstractItemView.NoSelection)
        table.verticalHeader().setVisible(False)
        table.setAlternatingRowColors(True)
        table.setShowGrid(True)
        table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        table.verticalHeader().setDefaultSectionSize(28)
        table.itemDoubleClicked.connect(self._handle_item_double_clicked)

        header = table.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignCenter)
        header.setSectionsMovable(False)
        header.setStretchLastSection(False)

        for column in range(len(headers)):
            if column == 1:
                header.setSectionResizeMode(column, QHeaderView.Stretch)
            else:
                header.setSectionResizeMode(column, QHeaderView.Fixed)

        table.setColumnWidth(0, 42)

        if len(headers) == 7:
            table.setColumnWidth(2, 86)
            table.setColumnWidth(3, 58)
            table.setColumnWidth(4, 58)
            table.setColumnWidth(5, 78)
            table.setColumnWidth(6, 118)
        elif len(headers) >= 6:
            table.setColumnWidth(2, 90)
            table.setColumnWidth(3, 120)
            table.setColumnWidth(4, 62)
            table.setColumnWidth(5, 118)

        return table

    def set_active_tab(self, index: int):
        self.stack.setCurrentIndex(index)

        for tab_index, button in self.tab_buttons.items():
            is_active = tab_index == index
            button.setProperty("active", is_active)
            button.style().unpolish(button)
            button.style().polish(button)

    def update_recent_activity(self, data: dict):
        self.current_data = data

        self._update_artist_table("recent_viewed_artists")
        self._update_artist_table("recent_registered_artists")
        self._update_artist_table("recent_checked_artists")
        self._update_update_history_table()
        self._update_error_history_table()
        self._update_missing_increased_table()

    def _update_artist_table(
        self,
        key: str,
    ):
        table = self.tables[key]
        artists = self.current_data.get(key, [])
        date_field = table.property("date_field")

        table.setRowCount(max(12, len(artists)))

        for row in range(table.rowCount()):
            if row >= len(artists):
                values = ["-", "-", "-", "-", "-", "-", "-"]
                tooltips = {}
                artist_id = None
            else:
                artist = artists[row]
                artist_name = str(artist.get("artist_name", "") or "-")
                values = [
                    str(row + 1),
                    self._shorten_text(artist_name, limit=18),
                    str(artist.get("pixiv_id", "") or "-"),
                    str(to_int(artist.get("folder_artwork_count", 0))),
                    str(to_int(artist.get("folder_file_count", 0))),
                    format_bytes(artist.get("folder_size_bytes", 0)),
                    format_datetime_short(artist.get(date_field)),
                ]
                tooltips = {1: artist_name}
                artist_id = artist.get("id")

            self._set_row_values(table, row, values, tooltips, artist_id)

    def _update_update_history_table(self):
        key = "recent_update_histories"
        table = self.tables[key]
        histories = self.current_data.get(key, [])

        table.setRowCount(max(12, len(histories)))

        for row in range(table.rowCount()):
            if row >= len(histories):
                values = ["-", "-", "-", "-", "-", "-"]
                tooltips = {}
                artist_id = None
            else:
                history = histories[row]
                artist_name = str(history.get("artist_name", "") or "-")
                values = [
                    str(row + 1),
                    self._shorten_text(artist_name, limit=18),
                    str(history.get("pixiv_id", "") or "-"),
                    str(history.get("result_label", "") or "-"),
                    str(to_int(history.get("missing_count", 0))),
                    format_datetime_short(history.get("checked_at")),
                ]
                tooltips = {1: artist_name}
                artist_id = history.get("artist_id")

            self._set_row_values(table, row, values, tooltips, artist_id)

    def _update_error_history_table(self):
        key = "recent_error_histories"
        table = self.tables[key]
        histories = self.current_data.get(key, [])

        table.setRowCount(max(12, len(histories)))

        for row in range(table.rowCount()):
            if row >= len(histories):
                values = ["-", "-", "-", "-", "-", "-"]
                tooltips = {}
                artist_id = None
            else:
                history = histories[row]
                artist_name = str(history.get("artist_name", "") or "-")
                error_reason = str(history.get("error_reason", "") or "-")
                values = [
                    str(row + 1),
                    self._shorten_text(artist_name, limit=18),
                    str(history.get("pixiv_id", "") or "-"),
                    str(history.get("result_label", "") or "확인 실패"),
                    self._shorten_text(error_reason, limit=16),
                    format_datetime_short(history.get("checked_at")),
                ]
                tooltips = {
                    1: artist_name,
                    4: error_reason,
                }
                artist_id = history.get("artist_id")

            self._set_row_values(table, row, values, tooltips, artist_id)

    def _update_missing_increased_table(self):
        key = "missing_increased_histories"
        table = self.tables[key]
        histories = self.current_data.get(key, [])

        table.setRowCount(max(12, len(histories)))

        for row in range(table.rowCount()):
            if row >= len(histories):
                values = ["-", "-", "-", "-", "-", "-"]
                tooltips = {}
                artist_id = None
            else:
                history = histories[row]
                artist_name = str(history.get("artist_name", "") or "-")
                missing_ids = format_missing_ids(
                    history.get("new_missing_ids", "")
                )
                values = [
                    str(row + 1),
                    self._shorten_text(artist_name, limit=18),
                    str(history.get("pixiv_id", "") or "-"),
                    str(to_int(history.get("missing_count", 0))),
                    format_signed_number(history.get("missing_delta", 0)),
                    missing_ids,
                ]
                tooltips = {
                    1: artist_name,
                    5: missing_ids,
                }
                artist_id = history.get("artist_id")

            self._set_row_values(table, row, values, tooltips, artist_id)

    def _set_row_values(
        self,
        table: QTableWidget,
        row: int,
        values: list[str],
        tooltips: dict[int, str] | None = None,
        artist_id=None,
    ):
        if tooltips is None:
            tooltips = {}

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
        limit: int = 18,
    ) -> str:
        if len(text) <= limit:
            return text

        return f"{text[:limit]}..."
