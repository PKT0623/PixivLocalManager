from PySide6.QtCore import Qt, Signal
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
    "확인 완료": "#0d6bfd",
    "스킵": "#6c757d",
    "일시정지": "#0dcaf0",
    "재개": "#6610f2",
    "재스캔": "#20c997",
}


class UpdateLogTable(QTableWidget):
    artist_detail_requested = Signal(int)
    selection_changed = Signal()

    HEADERS = [
        "시간",
        "진행",
        "결과",
        "작가명",
        "Pixiv ID",
        "로컬",
        "Pixiv",
        "누락",
        "누락 ID",
        "다운 예정",
        "상태",
    ]

    def __init__(self):
        super().__init__()

        self.log_rows = []
        self.current_filter = "전체"

        self._setup_ui()
        self.itemSelectionChanged.connect(self.selection_changed.emit)
        self.cellDoubleClicked.connect(self._handle_cell_double_clicked)

    def _setup_ui(self):
        self.setColumnCount(len(self.HEADERS))
        self.setHorizontalHeaderLabels(self.HEADERS)

        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setAlternatingRowColors(True)
        self.setSortingEnabled(False)
        self.verticalHeader().setVisible(False)

        header = self.horizontalHeader()
        header.setStretchLastSection(False)

        for index in range(len(self.HEADERS)):
            header.setSectionResizeMode(index, QHeaderView.ResizeToContents)

        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(8, QHeaderView.Stretch)
        header.setSectionResizeMode(9, QHeaderView.Stretch)

    def add_log_row(
        self,
        row_data: dict,
    ):
        normalized_row = dict(row_data)
        normalized_row["missing_ids"] = self._normalize_id_list(
            normalized_row.get("missing_ids", [])
        )
        normalized_row["download_candidate_ids"] = self._normalize_id_list(
            normalized_row.get("download_candidate_ids", [])
        )

        self.log_rows.append(normalized_row)
        self.refresh_rows()

    def clear_logs(self):
        self.log_rows = []
        self.setRowCount(0)

    def set_filter(
        self,
        filter_name: str,
    ):
        self.current_filter = filter_name
        self.refresh_rows()

    def refresh_rows(self):
        self.setRowCount(0)

        for row_data in self.log_rows:
            if not self._should_show_row(row_data):
                continue

            self._append_visible_row(row_data)

    def get_selected_log(self) -> dict | None:
        selected_rows = self.selectionModel().selectedRows()

        if not selected_rows:
            return None

        row = selected_rows[0].row()
        item = self.item(row, 0)

        if item is None:
            return None

        row_data = item.data(Qt.UserRole)

        if not isinstance(row_data, dict):
            return None

        return row_data

    def get_selected_artist_ids(self) -> list[int]:
        artist_ids = []

        for selected_row in self.selectionModel().selectedRows():
            row = selected_row.row()
            row_data = self._get_visible_row_data(row)

            if not row_data:
                continue

            artist_id = self._to_int(row_data.get("artist_id"))

            if artist_id is None:
                continue

            if artist_id in artist_ids:
                continue

            artist_ids.append(artist_id)

        return artist_ids

    def get_missing_artist_ids(self) -> list[int]:
        artist_ids = []

        for row_data in self.log_rows:
            artist_id = self._to_int(row_data.get("artist_id"))

            if artist_id is None:
                continue

            missing_ids = self._normalize_id_list(row_data.get("missing_ids"))

            if not missing_ids:
                continue

            if artist_id in artist_ids:
                continue

            artist_ids.append(artist_id)

        return artist_ids

    def get_error_artist_ids(self) -> list[int]:
        artist_ids = []

        for row_data in self.log_rows:
            artist_id = self._to_int(row_data.get("artist_id"))

            if artist_id is None:
                continue

            result = str(row_data.get("result", "") or "")

            if result != "오류":
                continue

            if artist_id in artist_ids:
                continue

            artist_ids.append(artist_id)

        return artist_ids

    def get_download_candidate_rows(self) -> list[dict]:
        rows = []

        for row_data in self.log_rows:
            download_candidate_ids = self._normalize_id_list(
                row_data.get("download_candidate_ids")
            )

            if not download_candidate_ids:
                continue

            normalized_row = dict(row_data)
            normalized_row["download_candidate_ids"] = download_candidate_ids
            rows.append(normalized_row)

        return rows

    def get_csv_data(self) -> tuple[list[str], list[list[str]]]:
        rows = []

        for row_data in self.log_rows:
            rows.append(
                [
                    str(row_data.get("time", "-")),
                    str(row_data.get("progress", "-")),
                    str(row_data.get("result", "-")),
                    str(row_data.get("artist_name", "-")),
                    str(row_data.get("pixiv_id", "-")),
                    str(row_data.get("local_count", "-")),
                    str(row_data.get("pixiv_count", "-")),
                    str(row_data.get("missing_count", "-")),
                    self._format_id_list(row_data.get("missing_ids", [])),
                    self._format_id_list(
                        row_data.get("download_candidate_ids", [])
                    ),
                    str(row_data.get("status", "-")),
                ]
            )

        return self.HEADERS.copy(), rows

    def select_log_by_artist_id(
        self,
        artist_id: int,
    ) -> bool:
        for row in range(self.rowCount()):
            item = self.item(row, 0)

            if item is None:
                continue

            row_data = item.data(Qt.UserRole)

            if not isinstance(row_data, dict):
                continue

            if row_data.get("artist_id") != artist_id:
                continue

            self.selectRow(row)
            self.scrollToItem(
                item,
                QAbstractItemView.PositionAtCenter,
            )
            return True

        return False

    def _should_show_row(
        self,
        row_data: dict,
    ) -> bool:
        result = str(row_data.get("result", ""))

        if self.current_filter == "전체":
            return True

        return result == self.current_filter

    def _append_visible_row(
        self,
        row_data: dict,
    ):
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
            self._format_id_list(row_data.get("missing_ids", [])),
            self._format_id_list(row_data.get("download_candidate_ids", [])),
            row_data.get("status", "-"),
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
        if column in (0, 1, 2, 4, 5, 6, 7, 10):
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

        if column != 2:
            return

        color = RESULT_COLORS.get(result)

        if color is None:
            return

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

        artist_id = row_data.get("artist_id")

        if artist_id is None:
            return

        self.artist_detail_requested.emit(int(artist_id))

    def _get_visible_row_data(
        self,
        row: int,
    ) -> dict | None:
        if row < 0 or row >= self.rowCount():
            return None

        item = self.item(row, 0)

        if item is None:
            return None

        row_data = item.data(Qt.UserRole)

        if not isinstance(row_data, dict):
            return None

        return row_data

    def _normalize_id_list(
        self,
        value,
    ) -> list[str]:
        if value is None:
            return []

        if isinstance(value, (list, tuple, set)):
            items = value
        else:
            text = str(value).strip()

            if not text:
                return []

            items = text.replace("\n", ",").split(",")

        normalized_items = []

        for item in items:
            text = str(item).strip()

            if not text or text == "-":
                continue

            normalized_items.append(text)

        return normalized_items

    def _format_id_list(
        self,
        value,
    ) -> str:
        return ", ".join(self._normalize_id_list(value))

    def _to_int(
        self,
        value,
    ) -> int | None:
        try:
            return int(value)
        except (TypeError, ValueError):
            return None
