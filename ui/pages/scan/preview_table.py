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
    "제외": "#adb5bd",
}


class ScanPreviewTable(QTableWidget):
    selection_changed = Signal(dict)

    def __init__(self):
        super().__init__()

        self.preview_rows = []
        self.filtered_rows = []
        self.show_created_only = False
        self.show_updated_only = False
        self.show_error_only = False
        self.hide_unchanged = True

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
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
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
        self.preview_rows = [
            self._normalize_preview_row(row)
            for row in rows
        ]

        self.apply_filters()

    def append_preview_rows(
        self,
        rows: list[dict],
    ):
        normalized_rows = [
            self._normalize_preview_row(row)
            for row in rows
        ]

        self.preview_rows.extend(normalized_rows)
        self.apply_filters()

    def set_filters(
        self,
        show_created_only: bool,
        show_updated_only: bool,
        show_error_only: bool,
        hide_unchanged: bool,
    ):
        self.show_created_only = show_created_only
        self.show_updated_only = show_updated_only
        self.show_error_only = show_error_only
        self.hide_unchanged = hide_unchanged

        self.apply_filters()

    def apply_filters(self):
        self.filtered_rows = [
            row
            for row in self.preview_rows
            if self._matches_filters(row)
        ]

        self._render_rows(self.filtered_rows)

    def clear_preview(self):
        self.preview_rows = []
        self.filtered_rows = []
        self.setRowCount(0)
        self.selection_changed.emit(self.get_selected_summary())

    def select_all_available(self):
        self._set_available_checked(True)

    def clear_all_selection(self):
        self._set_available_checked(False)

    def exclude_error_rows(self):
        for row_data in self.preview_rows:
            if row_data.get("preview_result") == "오류 예상":
                row_data["is_excluded"] = True
                row_data["selected"] = False

        self.apply_filters()

    def exclude_selected_rows(self):
        selected_rows = self.selectionModel().selectedRows()

        if not selected_rows:
            return

        row_ids = self._get_view_row_ids(selected_rows)

        for row_data in self.preview_rows:
            if row_data.get("_row_id") in row_ids:
                row_data["is_excluded"] = True
                row_data["selected"] = False

        self.apply_filters()

    def keep_selected_rows_only(self):
        selected_rows = self.selectionModel().selectedRows()

        if not selected_rows:
            return

        row_ids = self._get_view_row_ids(selected_rows)

        for row_data in self.preview_rows:
            if row_data.get("_row_id") not in row_ids:
                row_data["is_excluded"] = True
                row_data["selected"] = False

        self.apply_filters()

    def get_selected_folder_paths(self) -> list[str]:
        folder_paths = []

        for row_data in self.preview_rows:
            if row_data.get("is_excluded"):
                continue

            if row_data.get("selected") is not True:
                continue

            if row_data.get("can_scan") is not True:
                continue

            folder_path = str(row_data.get("folder_path", "") or "").strip()

            if folder_path:
                folder_paths.append(folder_path)

        return folder_paths

    def get_all_preview_rows(self) -> list[dict]:
        rows = []

        for row_data in self.preview_rows:
            item = dict(row_data)
            item.pop("_row_id", None)
            item["selected"] = "1" if item.get("selected") else "0"
            item["is_excluded"] = "1" if item.get("is_excluded") else "0"
            rows.append(item)

        return rows

    def get_selected_summary(self) -> dict:
        summary = {
            "created": 0,
            "updated": 0,
            "unchanged": 0,
            "failed": 0,
            "selected": 0,
        }

        for row_data in self.preview_rows:
            if row_data.get("is_excluded"):
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

            if row_data.get("selected") is True:
                summary["selected"] += 1

        return summary

    def _normalize_preview_row(
        self,
        row_data: dict,
    ) -> dict:
        item = dict(row_data)
        item["_row_id"] = id(item)
        item.setdefault("is_excluded", False)

        preview_result = str(item.get("preview_result", "") or "")
        can_scan = bool(item.get("can_scan", False))

        auto_checked_results = {
            "신규 등록 예정",
            "업데이트 예정",
        }

        item["selected"] = (
            can_scan
            and preview_result in auto_checked_results
        )

        return item

    def _matches_filters(
        self,
        row_data: dict,
    ) -> bool:
        if row_data.get("is_excluded"):
            return False

        result = str(row_data.get("preview_result", "") or "")
        active_result_filters = self._get_active_result_filters()

        if active_result_filters and result not in active_result_filters:
            return False

        if self.hide_unchanged and result == "변경 없음 예정":
            return False

        return True

    def _get_active_result_filters(self) -> set[str]:
        result_filters = set()

        if self.show_created_only:
            result_filters.add("신규 등록 예정")

        if self.show_updated_only:
            result_filters.add("업데이트 예정")

        if self.show_error_only:
            result_filters.add("오류 예상")

        return result_filters

    def _render_rows(
        self,
        rows: list[dict],
    ):
        self.blockSignals(True)
        self.setRowCount(0)

        for row_data in rows:
            self._append_row(row_data)

        self.blockSignals(False)
        self.selection_changed.emit(self.get_selected_summary())

    def _set_available_checked(
        self,
        checked: bool,
    ):
        visible_row_ids = {
            row.get("_row_id")
            for row in self.filtered_rows
        }

        for row_data in self.preview_rows:
            if row_data.get("_row_id") not in visible_row_ids:
                continue

            if row_data.get("is_excluded"):
                continue

            if row_data.get("can_scan") is not True:
                continue

            row_data["selected"] = checked

        self.apply_filters()

    def _append_row(
        self,
        row_data: dict,
    ):
        row = self.rowCount()
        self.insertRow(row)

        can_scan = bool(row_data.get("can_scan", False))
        is_excluded = bool(row_data.get("is_excluded", False))
        is_selected = bool(row_data.get("selected", False))

        check_item = QTableWidgetItem("")
        check_item.setData(Qt.UserRole, row_data)
        check_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)

        if can_scan and not is_excluded:
            check_item.setFlags(
                Qt.ItemIsEnabled
                | Qt.ItemIsUserCheckable
                | Qt.ItemIsSelectable
            )
            check_item.setCheckState(
                Qt.Checked if is_selected else Qt.Unchecked
            )
        else:
            check_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            check_item.setCheckState(Qt.Unchecked)

        self.setItem(row, 0, check_item)

        values = [
            self._get_display_result(row_data),
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
            self._apply_item_color(item, index, values, is_excluded)
            self.setItem(row, index, item)

    def _get_display_result(
        self,
        row_data: dict,
    ) -> str:
        if row_data.get("is_excluded"):
            return "제외"

        return str(row_data.get("preview_result", "") or "-")

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
        is_excluded: bool,
    ):
        if is_excluded:
            item.setForeground(QColor("#666666"))
            item.setBackground(QColor("#f1f3f5"))
            return

        if column != 1:
            return

        result = values[0]
        color = PREVIEW_RESULT_COLORS.get(result)

        if color is None:
            return

        item.setForeground(QColor("#ffffff"))
        item.setBackground(QColor(color))

    def _get_view_row_ids(
        self,
        selected_rows,
    ) -> set:
        row_ids = set()

        for model_index in selected_rows:
            check_item = self.item(model_index.row(), 0)

            if check_item is None:
                continue

            row_data = check_item.data(Qt.UserRole)

            if not isinstance(row_data, dict):
                continue

            row_ids.add(row_data.get("_row_id"))

        return row_ids

    def _handle_item_changed(
        self,
        item: QTableWidgetItem,
    ):
        if item.column() != 0:
            return

        row_data = item.data(Qt.UserRole)

        if not isinstance(row_data, dict):
            return

        row_data["selected"] = item.checkState() == Qt.Checked
        self.selection_changed.emit(self.get_selected_summary())
