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
    "스킵": "#6c757d",
    "일시정지": "#0dcaf0",
    "재개": "#6610f2",
}


class UpdateLogTable(QTableWidget):
    HEADERS = [
        "시간",
        "진행",
        "결과",
        "작가명",
        "Pixiv ID",
        "로컬",
        "Pixiv",
        "누락",
        "변화",
        "신규",
        "해결",
        "누락 ID",
        "상태",
    ]

    def __init__(self):
        super().__init__()

        self.csv_rows = []

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
        header.setSectionResizeMode(8, QHeaderView.Fixed)
        header.setSectionResizeMode(9, QHeaderView.Fixed)
        header.setSectionResizeMode(10, QHeaderView.Fixed)
        header.setSectionResizeMode(11, QHeaderView.Fixed)
        header.setSectionResizeMode(12, QHeaderView.Fixed)

        self.setColumnWidth(0, 80)
        self.setColumnWidth(1, 50)
        self.setColumnWidth(2, 100)
        self.setColumnWidth(4, 90)
        self.setColumnWidth(5, 50)
        self.setColumnWidth(6, 50)
        self.setColumnWidth(7, 50)
        self.setColumnWidth(8, 50)
        self.setColumnWidth(9, 50)
        self.setColumnWidth(10, 50)
        self.setColumnWidth(11, 360)
        self.setColumnWidth(12, 140)

    def add_log_row(self, row_data: dict):
        row = self.rowCount()
        self.insertRow(row)

        missing_ids = row_data.get("missing_ids", "")
        missing_ids_display = self._format_missing_ids(missing_ids)
        missing_delta_display = self._format_missing_delta(row_data)

        values = [
            row_data.get("time", "-"),
            row_data.get("progress", "-"),
            row_data.get("result", "-"),
            row_data.get("artist_name", "-"),
            row_data.get("pixiv_id", "-"),
            row_data.get("local_count", "-"),
            row_data.get("pixiv_count", "-"),
            row_data.get("missing_count", "-"),
            missing_delta_display,
            row_data.get("new_missing_count", "-"),
            row_data.get("resolved_missing_count", "-"),
            missing_ids_display,
            row_data.get("status", "-"),
        ]

        csv_values = [
            row_data.get("time", "-"),
            row_data.get("progress", "-"),
            row_data.get("result", "-"),
            row_data.get("artist_name", "-"),
            row_data.get("pixiv_id", "-"),
            row_data.get("local_count", "-"),
            row_data.get("pixiv_count", "-"),
            row_data.get("missing_count", "-"),
            missing_delta_display,
            row_data.get("new_missing_count", "-"),
            row_data.get("resolved_missing_count", "-"),
            self._ids_to_excel_text(missing_ids),
            row_data.get("status", "-"),
        ]

        self.csv_rows.append(csv_values)

        for column, value in enumerate(values):
            item = QTableWidgetItem(str(value))

            if column in (3, 11):
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
        self.csv_rows = []
        super().setRowCount(0)

    def get_csv_data(self) -> tuple[list[str], list[list[str]]]:
        return self.HEADERS.copy(), self.csv_rows.copy()

    def _format_missing_delta(
        self,
        row_data: dict,
    ) -> str:
        if not row_data.get("has_previous", False):
            return "-"

        value = row_data.get("missing_delta", 0)

        try:
            delta = int(value)
        except (TypeError, ValueError):
            return str(value or "-")

        if delta > 0:
            return f"+{delta}"

        if delta < 0:
            return str(delta)

        return "0"

    def _format_missing_ids(
        self,
        values,
    ) -> str:
        ids = self._parse_ids(values)

        if not ids:
            return "-"

        if len(ids) <= 5:
            return ", ".join(ids)

        recent_ids = ids[:3]
        remain_count = len(ids) - len(recent_ids)

        return f"{', '.join(recent_ids)} 외 {remain_count}개"

    def _ids_to_excel_text(
        self,
        values,
    ) -> str:
        ids_text = self._ids_to_text(values)

        if not ids_text:
            return ""

        safe_text = ids_text.replace('"', '""')

        return f'="{safe_text}"'

    def _ids_to_text(
        self,
        values,
    ) -> str:
        ids = self._parse_ids(values)

        if not ids:
            return ""

        return ", ".join(ids)

    def _parse_ids(
        self,
        values,
    ) -> list[str]:
        if not values:
            return []

        if isinstance(values, str):
            raw_values = values.split(",")
        else:
            raw_values = values

        return [
            str(value).strip()
            for value in raw_values
            if str(value).strip()
        ]
