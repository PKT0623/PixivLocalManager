from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QTableWidget,
    QTableWidgetItem,
)


RESULT_COLORS = {
    "가져오기": "#0d6efd",
    "저장": "#198754",
    "중복": "#6c757d",
    "오류": "#dc3545",
    "완료": "#198754",
    "시작": "#0d6efd",
    "성공": "#198754",
    "실패": "#dc3545",
    "재시도": "#fd7e14",
    "세션 오류": "#dc3545",
    "요청 제한": "#dc3545",
    "요약": "#6f42c1",
}


class PixivManagerLogTable(QTableWidget):
    HEADERS = [
        "시간",
        "구분",
        "결과",
        "내용",
        "신규",
        "파일 중복",
        "DB 중복",
        "오류",
    ]

    def __init__(self):
        super().__init__()

        self._setup_ui()

    def _setup_ui(self):
        self.setColumnCount(len(self.HEADERS))
        self.setHorizontalHeaderLabels(self.HEADERS)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.NoSelection)
        self.verticalHeader().setVisible(False)
        self.setSortingEnabled(False)
        self.setAlternatingRowColors(True)

        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.Fixed)
        header.setSectionResizeMode(5, QHeaderView.Fixed)
        header.setSectionResizeMode(6, QHeaderView.Fixed)
        header.setSectionResizeMode(7, QHeaderView.Fixed)

        self.setColumnWidth(0, 80)
        self.setColumnWidth(1, 90)
        self.setColumnWidth(2, 90)
        self.setColumnWidth(4, 70)
        self.setColumnWidth(5, 80)
        self.setColumnWidth(6, 80)
        self.setColumnWidth(7, 70)

    def add_log_row(
        self,
        row_data: dict,
    ):
        row = self.rowCount()
        self.insertRow(row)

        values = [
            row_data.get("time", "-"),
            row_data.get("target", "-"),
            row_data.get("result", "-"),
            row_data.get("message", "-"),
            row_data.get("new_count", "-"),
            row_data.get("duplicate_in_file_count", "-"),
            row_data.get("duplicate_existing_count", "-"),
            row_data.get("error_count", "-"),
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

    def clear_logs(self):
        self.setRowCount(0)
