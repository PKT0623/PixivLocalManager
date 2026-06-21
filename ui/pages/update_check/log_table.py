from PySide6.QtCore import QTimer, Qt, Signal
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
        "변화",
        "신규",
        "해결",
        "누락 ID",
        "상태",
    ]

    def __init__(self):
        super().__init__()

        self.csv_rows = []
        self.row_data_list = []
        self.auto_scroll_enabled = True

        self._setup_ui()

    def _setup_ui(self):
        self.setColumnCount(len(self.HEADERS))
        self.setHorizontalHeaderLabels(self.HEADERS)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
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

        self.itemDoubleClicked.connect(self._handle_item_double_clicked)
        self.itemSelectionChanged.connect(self.selection_changed.emit)

    def add_log_row(self, row_data: dict):
        row = self.rowCount()
        self.insertRow(row)

        row_payload = dict(row_data)
        self.row_data_list.append(row_payload)

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
            item.setData(Qt.UserRole, row_payload)

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

        self._schedule_scroll_to_bottom()

    def clear_logs(self):
        self.csv_rows = []
        self.row_data_list = []
        super().setRowCount(0)
        self.selection_changed.emit()

    def get_csv_data(self) -> tuple[list[str], list[list[str]]]:
        return self.HEADERS.copy(), self.csv_rows.copy()

    def get_selected_rows(self) -> list[dict]:
        selected_rows = {
            index.row()
            for index in self.selectionModel().selectedRows()
        }

        rows = []

        for row in sorted(selected_rows):
            if row < 0 or row >= len(self.row_data_list):
                continue

            rows.append(dict(self.row_data_list[row]))

        return rows

    def get_selected_artist_ids(self) -> list[int]:
        return self._collect_artist_ids(self.get_selected_rows())

    def get_missing_artist_ids(self) -> list[int]:
        rows = [
            row
            for row in self.row_data_list
            if self._has_missing_artworks(row)
        ]

        return self._collect_artist_ids(rows)

    def get_error_artist_ids(self) -> list[int]:
        rows = [
            row
            for row in self.row_data_list
            if row.get("result") == "오류"
        ]

        return self._collect_artist_ids(rows)

    def get_download_candidate_rows(self) -> list[dict]:
        rows = []

        for row in self.row_data_list:
            candidate_ids = self._parse_ids(
                row.get("download_candidate_ids")
                or row.get("missing_ids")
            )

            if not candidate_ids:
                continue

            item = dict(row)
            item["download_candidate_ids"] = candidate_ids
            rows.append(item)

        return rows

    def _schedule_scroll_to_bottom(self):
        if not self.auto_scroll_enabled:
            return

        QTimer.singleShot(0, self.scrollToBottom)

    def _collect_artist_ids(
        self,
        rows: list[dict],
    ) -> list[int]:
        artist_ids = []

        for row in rows:
            artist_id = row.get("artist_id")

            if artist_id is None:
                continue

            try:
                normalized_artist_id = int(artist_id)
            except (TypeError, ValueError):
                continue

            if normalized_artist_id in artist_ids:
                continue

            artist_ids.append(normalized_artist_id)

        return artist_ids

    def _has_missing_artworks(
        self,
        row: dict,
    ) -> bool:
        missing_ids = self._parse_ids(row.get("missing_ids"))

        if missing_ids:
            return True

        try:
            return int(row.get("missing_count", 0) or 0) > 0
        except (TypeError, ValueError):
            return False

    def _handle_item_double_clicked(
        self,
        item: QTableWidgetItem,
    ):
        row_data = item.data(Qt.UserRole)

        if not isinstance(row_data, dict):
            return

        artist_id = row_data.get("artist_id")

        if artist_id is None:
            return

        try:
            self.artist_detail_requested.emit(int(artist_id))
        except (TypeError, ValueError):
            return

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
