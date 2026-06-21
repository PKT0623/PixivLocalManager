from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QTableWidget,
)


class RecentActivityTableFactoryMixin:
    def _setup_activity_tables(self):
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
        self._set_table_column_widths(table, len(headers))

        return table

    def _set_table_column_widths(
        self,
        table: QTableWidget,
        header_count: int,
    ):
        if header_count == 7:
            table.setColumnWidth(2, 86)
            table.setColumnWidth(3, 58)
            table.setColumnWidth(4, 58)
            table.setColumnWidth(5, 78)
            table.setColumnWidth(6, 118)
            return

        if header_count >= 6:
            table.setColumnWidth(2, 90)
            table.setColumnWidth(3, 120)
            table.setColumnWidth(4, 62)
            table.setColumnWidth(5, 118)
