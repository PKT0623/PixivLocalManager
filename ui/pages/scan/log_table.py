from PySide6.QtCore import Qt, Signal
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
    "변경 없음": "#6c757d",
    "경고": "#fd7e14",
    "오류": "#dc3545",
    "제외": "#6c757d",
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
    artist_open_requested = Signal(int)
    folder_open_requested = Signal(str)

    def __init__(self):
        super().__init__()

        self.all_rows = []
        self.result_filter = "전체"
        self.error_only = False

        self._setup_ui()
        self.cellDoubleClicked.connect(self._handle_cell_double_clicked)

    def _setup_ui(self):
        self.setColumnCount(9)
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
                "상세 내용",
            ]
        )
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
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
        header.setSectionResizeMode(8, QHeaderView.Stretch)

    def add_log_row(self, row_data: dict):
        self.all_rows.append(dict(row_data))
        self.refresh_rows()

    def add_info_log(self, message: str):
        from .log_utils import build_info_log_row

        self.add_log_row(
            build_info_log_row(message)
        )

    def clear_log(self):
        self.all_rows = []
        self.setRowCount(0)

    def set_result_filter(self, result_filter: str):
        self.result_filter = result_filter
        self.refresh_rows()

    def set_error_only(self, error_only: bool):
        self.error_only = error_only
        self.refresh_rows()

    def get_failed_rows(self) -> list[dict]:
        return [
            row
            for row in self.all_rows
            if row.get("result") == "실패"
        ]

    def clear_failed_rows(self):
        self.all_rows = [
            row
            for row in self.all_rows
            if row.get("result") != "실패"
        ]
        self.refresh_rows()

    def refresh_rows(self):
        self.setRowCount(0)

        for row_data in self.all_rows:
            if not self._should_show_row(row_data):
                continue

            self._append_visible_row(row_data)

    def _should_show_row(self, row_data: dict) -> bool:
        result = str(row_data.get("result", ""))

        if self.error_only and result not in ("실패", "오류"):
            return False

        if self.result_filter != "전체" and result != self.result_filter:
            return False

        return True

    def _append_visible_row(self, row_data: dict):
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
            row_data.get("error_message", "-"),
        ]

        for column, value in enumerate(values):
            item = QTableWidgetItem(str(value))
            item.setData(Qt.UserRole, row_data)
            self._apply_item_alignment(item, column)
            self._apply_item_color(item, column, values)
            self.setItem(row, column, item)

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

    def _handle_cell_double_clicked(
        self,
        row: int,
        column: int,
    ):
        item = self.item(row, column)

        if item is None:
            return

        row_data = item.data(Qt.UserRole)

        if not isinstance(row_data, dict):
            return

        if row_data.get("result") in ("실패", "오류", "경고", "제외"):
            folder_path = str(row_data.get("folder_path", "") or "").strip()

            if folder_path:
                self.folder_open_requested.emit(folder_path)

            return

        artist_id = row_data.get("artist_id")

        if artist_id is None:
            return

        self.artist_open_requested.emit(int(artist_id))
