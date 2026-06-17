from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QHeaderView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from .utils import format_datetime_short, to_int


class ScanStatisticsSection(QFrame):
    def __init__(self):
        super().__init__()

        self.setObjectName("detailCard")
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(8)

        title_label = QLabel("스캔 통계")
        title_label.setObjectName("sectionTitle")

        self.result_table = QTableWidget()
        self.result_table.setColumnCount(5)
        self.result_table.setHorizontalHeaderLabels(
            [
                "No",
                "작가명",
                "결과",
                "누락",
                "확인일",
            ]
        )
        self.result_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.result_table.setSelectionMode(QAbstractItemView.NoSelection)
        self.result_table.verticalHeader().setVisible(False)
        self.result_table.setAlternatingRowColors(True)
        self.result_table.setShowGrid(True)
        self.result_table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.result_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.result_table.verticalHeader().setDefaultSectionSize(26)

        header = self.result_table.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignCenter)
        header.setSectionResizeMode(0, QHeaderView.Interactive)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Interactive)
        header.setSectionResizeMode(3, QHeaderView.Interactive)
        header.setSectionResizeMode(4, QHeaderView.Interactive)

        self.result_table.setColumnWidth(0, 42)
        self.result_table.setColumnWidth(1, 96)
        self.result_table.setColumnWidth(2, 110)
        self.result_table.setColumnWidth(3, 52)
        self.result_table.setColumnWidth(4, 112)

        layout.addWidget(title_label)
        layout.addWidget(self.result_table, 1)

    def update_scan_statistics(self, data: dict):
        recent_results = data.get("recent_scan_results", [])
        row_count = max(5, len(recent_results))

        self.result_table.setRowCount(row_count)

        for row in range(row_count):
            if row >= len(recent_results):
                values = ["-", "-", "-", "-", "-"]
                tooltips = {}
            else:
                history = recent_results[row]
                artist_name = str(history.get("artist_name", "") or "-")
                result_label = str(history.get("result_label", "") or "-")
                values = [
                    str(row + 1),
                    self._shorten_text(artist_name, limit=12),
                    self._shorten_text(result_label, limit=10),
                    str(to_int(history.get("missing_count", 0))),
                    format_datetime_short(history.get("checked_at")),
                ]
                tooltips = {
                    1: artist_name,
                    2: result_label,
                }

            self._set_row_values(row, values, tooltips)

    def _set_row_values(
        self,
        row: int,
        values: list[str],
        tooltips: dict[int, str] | None = None,
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

            self.result_table.setItem(row, column, item)

    def _shorten_text(
        self,
        text: str,
        limit: int = 14,
    ) -> str:
        if len(text) <= limit:
            return text

        return f"{text[:limit]}..."
