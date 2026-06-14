from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QTableWidget,
    QTableWidgetItem,
)


RESULT_COLORS = {
    "최신": "#198754",
    "업데이트 필요": "#fd7e14",
    "미확인": "#6c757d",
    "오류": "#dc3545",
    "휴식": "#0d6efd",
    "취소됨": "#6c757d",
    "확인 완료": "#0d6efd",
}


class UpdateLogTable(QTableWidget):
    def __init__(self):
        super().__init__()

        self._setup_ui()

    def _setup_ui(self):
        self.setColumnCount(9)
        self.setHorizontalHeaderLabels(
            [
                "시간",
                "진행",
                "결과",
                "작가명",
                "Pixiv ID",
                "로컬",
                "Pixiv",
                "누락",
                "상태",
            ]
        )
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.NoSelection)
        self.verticalHeader().setVisible(False)
        self.setSortingEnabled(False)
        self.setAlternatingRowColors(True)

        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(8, QHeaderView.ResizeToContents)

    def add_log_row(self, row_data: dict):
        row = self.rowCount()
        self.insertRow(row)

        values = [
            row_data.get("time", "-"),
            row_data.get("progress", "-"),
            row_data.get("result", "-"),
            row_data.get("artist_name", "-"),
            row_data.get("pixiv_id", "-"),
            row_data.get("local_count", "-"),
            row_data.get("pixiv_count", "-"),
            row_data.get("missing_count", "-"),
            row_data.get("status", "-"),
        ]

        for column, value in enumerate(values):
            item = QTableWidgetItem(str(value))

            if column == 3:
                item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            else:
                item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)

            if column == 2:
                color = RESULT_COLORS.get(str(value))

                if color:
                    item.setBackground(QColor(color))
                    item.setForeground(QColor("white"))

            self.setItem(row, column, item)

        self.scrollToBottom()
