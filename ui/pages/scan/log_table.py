from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QTableWidget,
    QTableWidgetItem,
)


RESULT_COLORS = {
    "등록": "#198754",
    "업데이트": "#0d6efd",
    "실패": "#dc3545",
    "정보": "#6c757d",
}

STATUS_COLORS = {
    "unknown": "#6c757d",
    "latest": "#198754",
    "up_to_date": "#198754",
    "need_update": "#fd7e14",
    "updated": "#0d6efd",
    "error": "#dc3545",
}


class ScanLogTable(QTableWidget):
    def __init__(self):
        super().__init__()

        self._setup_ui()

    def _setup_ui(self):
        self.setColumnCount(8)
        self.setHorizontalHeaderLabels(
            [
                "시간",
                "진행",
                "결과",
                "작가명",
                "Pixiv ID",
                "작품 수",
                "파일 수",
                "상태",
            ]
        )
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.NoSelection)
        self.setSortingEnabled(False)
        self.verticalHeader().setVisible(False)
        self.setAlternatingRowColors(True)
        self.setShowGrid(True)
        self.verticalHeader().setDefaultSectionSize(30)

        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)

    def add_log_row(self, row_data: dict):
        row = self.rowCount()
        self.insertRow(row)

        values = [
            row_data.get("time", "-"),
            row_data.get("progress", "-"),
            row_data.get("result", "-"),
            row_data.get("artist_name", "-"),
            row_data.get("pixiv_id", "-"),
            row_data.get("artwork_count", "-"),
            row_data.get("file_count", "-"),
            row_data.get("update_status", "-"),
        ]

        for column, value in enumerate(values):
            item = QTableWidgetItem(str(value))
            self._apply_item_alignment(item, column)
            self._apply_item_color(item, column, values)
            self.setItem(row, column, item)

        self.scrollToBottom()

    def add_info_log(self, message: str):
        from .log_utils import build_info_log_row

        self.add_log_row(
            build_info_log_row(message)
        )

    def clear_log(self):
        self.setRowCount(0)

    def _apply_item_alignment(
        self,
        item: QTableWidgetItem,
        column: int,
    ):
        if column in (0, 1, 2, 4, 5, 6, 7):
            item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        else:
            item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)

    def _apply_item_color(
        self,
        item: QTableWidgetItem,
        column: int,
        values: list,
    ):
        result = values[2]
        status = values[7]

        if column == 2:
            color = RESULT_COLORS.get(result)

            if color is not None:
                item.setForeground(QColor("#ffffff"))
                item.setBackground(QColor(color))

        if column == 7:
            color = STATUS_COLORS.get(status)

            if color is not None:
                item.setForeground(QColor("#ffffff"))
                item.setBackground(QColor(color))
