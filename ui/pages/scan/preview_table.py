from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QTableWidget,
    QTableWidgetItem,
)

from .preview_table_parts import (
    build_preview_summary,
    matches_preview_filters,
    render_preview_rows,
)


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
            if matches_preview_filters(
                row_data=row,
                show_created_only=self.show_created_only,
                show_updated_only=self.show_updated_only,
                show_error_only=self.show_error_only,
                hide_unchanged=self.hide_unchanged,
            )
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
        return build_preview_summary(self.preview_rows)

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

    def _render_rows(
        self,
        rows: list[dict],
    ):
        render_preview_rows(self, rows)
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
