from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QTableWidget,
    QTableWidgetItem,
)


PREVIEW_RESULT_COLORS = {
    "신규 등록 예정": "#198754",
    "업데이트 예정": "#0d6efd",
    "변경 없음 예정": "#6c757d",
    "오류 예상": "#dc3545",
}


class ScanPreviewTable(QTableWidget):
    selection_changed = Signal(dict)

    def __init__(self):
        super().__init__()

        self.preview_rows = []

        self._setup_ui()
        self.itemChanged.connect(self._handle_item_changed)

    def _setup_ui(self):
        self.setColumnCount(8)
        self.setHorizontalHeaderLabels(
            [
                "선택",
                "예상 결과",
                "작가명",
                "Pixiv ID",
                "작품 수",
                "파일 수",
                "폴더 경로",
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
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.Stretch)
        header.setSectionResizeMode(7, QHeaderView.Stretch)

    def set_preview_rows(
        self,
        rows: list[dict],
    ):
        self.blockSignals(True)

        self.preview_rows = [
            dict(row)
            for row in rows
        ]

        self.setRowCount(0)

        for row_data in self.preview_rows:
            self._append_row(row_data)

        self.blockSignals(False)
        self.selection_changed.emit(self.get_selected_summary())

    def clear_preview(self):
        self.preview_rows = []
        self.setRowCount(0)
        self.selection_changed.emit(self.get_selected_summary())

    def select_all_available(self):
        self._set_available_checked(True)

    def clear_all_selection(self):
        self._set_available_checked(False)

    def exclude_error_rows(self):
        self.blockSignals(True)

        for row in range(self.rowCount()):
            result_item = self.item(row, 1)
            check_item = self.item(row, 0)

            if result_item is None or check_item is None:
                continue

            if result_item.text() == "오류 예상":
                check_item.setCheckState(Qt.Unchecked)

        self.blockSignals(False)
        self.selection_changed.emit(self.get_selected_summary())

    def get_selected_folder_paths(self) -> list[str]:
        folder_paths = []

        for row in range(self.rowCount()):
            check_item = self.item(row, 0)

            if check_item is None:
                continue

            if check_item.checkState() != Qt.Checked:
                continue

            row_data = check_item.data(Qt.UserRole)

            if not isinstance(row_data, dict):
                continue

            if row_data.get("can_scan") is not True:
                continue

            folder_path = str(row_data.get("folder_path", "") or "").strip()

            if folder_path:
                folder_paths.append(folder_path)

        return folder_paths

    def get_selected_summary(self) -> dict:
        summary = {
            "created": 0,
            "updated": 0,
            "unchanged": 0,
            "failed": 0,
            "selected": 0,
        }

        for row in range(self.rowCount()):
            check_item = self.item(row, 0)

            if check_item is None:
                continue

            row_data = check_item.data(Qt.UserRole)

            if not isinstance(row_data, dict):
                continue

            result = str(row_data.get("preview_result", "") or "")

            if result == "신규 등록 예정":
                summary["created"] += 1
            elif result == "업데이트 예정":
                summary["updated"] += 1
            elif result == "변경 없음 예정":
                summary["unchanged"] += 1
            elif result == "오류 예상":
                summary["failed"] += 1

            if check_item.checkState() == Qt.Checked:
                summary["selected"] += 1

        return summary

    def _set_available_checked(
        self,
        checked: bool,
    ):
        self.blockSignals(True)

        for row in range(self.rowCount()):
            check_item = self.item(row, 0)

            if check_item is None:
                continue

            row_data = check_item.data(Qt.UserRole)

            if not isinstance(row_data, dict):
                continue

            if row_data.get("can_scan") is not True:
                continue

            check_item.setCheckState(
                Qt.Checked if checked else Qt.Unchecked
            )

        self.blockSignals(False)
        self.selection_changed.emit(self.get_selected_summary())

    def _append_row(
        self,
        row_data: dict,
    ):
        row = self.rowCount()
        self.insertRow(row)

        can_scan = bool(row_data.get("can_scan", False))

        check_item = QTableWidgetItem("")
        check_item.setData(Qt.UserRole, row_data)
        check_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)

        auto_checked_results = {
            "신규 등록 예정",
            "업데이트 예정",
        }

        preview_result = str(row_data.get("preview_result", "") or "")
        should_check = can_scan and preview_result in auto_checked_results

        if can_scan:
            check_item.setFlags(
                Qt.ItemIsEnabled
                | Qt.ItemIsUserCheckable
                | Qt.ItemIsSelectable
            )
            check_item.setCheckState(
                Qt.Checked if should_check else Qt.Unchecked
            )
        else:
            check_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            check_item.setCheckState(Qt.Unchecked)

        self.setItem(row, 0, check_item)

        values = [
            row_data.get("preview_result", "-"),
            row_data.get("artist_name", "-"),
            row_data.get("pixiv_id", "-"),
            row_data.get("artwork_count", "-"),
            row_data.get("file_count", "-"),
            row_data.get("folder_path", "-"),
            row_data.get("message", "-"),
        ]

        for index, value in enumerate(values, start=1):
            item = QTableWidgetItem(str(value))
            item.setData(Qt.UserRole, row_data)
            self._apply_item_alignment(item, index)
            self._apply_item_color(item, index, values)
            self.setItem(row, index, item)

    def _apply_item_alignment(
        self,
        item: QTableWidgetItem,
        column: int,
    ):
        if column in (0, 1, 3, 4, 5):
            item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        else:
            item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)

    def _apply_item_color(
        self,
        item: QTableWidgetItem,
        column: int,
        values: list,
    ):
        if column != 1:
            return

        result = values[0]
        color = PREVIEW_RESULT_COLORS.get(result)

        if color is None:
            return

        item.setForeground(QColor("#ffffff"))
        item.setBackground(QColor(color))

    def _handle_item_changed(
        self,
        item: QTableWidgetItem,
    ):
        if item.column() != 0:
            return

        self.selection_changed.emit(self.get_selected_summary())
