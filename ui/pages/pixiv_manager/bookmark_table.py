import json
import webbrowser
from datetime import datetime

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtWidgets import (
    QAbstractItemDelegate,
    QAbstractItemView,
    QHeaderView,
    QStyle,
    QStyleOptionButton,
    QTableView,
)


SYNC_STATUS_LABELS = {
    "pending": "대기",
    "synced": "완료",
    "failed": "실패",
    "skipped": "스킵",
}


class CenterCheckBoxDelegate(QAbstractItemDelegate):
    def paint(
        self,
        painter,
        option,
        index,
    ):
        checked = index.data(Qt.CheckStateRole) == Qt.Checked

        checkbox_option = QStyleOptionButton()
        checkbox_option.state = QStyle.State_Enabled

        if checked:
            checkbox_option.state |= QStyle.State_On
        else:
            checkbox_option.state |= QStyle.State_Off

        checkbox_rect = option.widget.style().subElementRect(
            QStyle.SE_CheckBoxIndicator,
            checkbox_option,
            option.widget,
        )

        checkbox_option.rect = checkbox_rect
        checkbox_option.rect.moveCenter(option.rect.center())

        option.widget.style().drawControl(
            QStyle.CE_CheckBox,
            checkbox_option,
            painter,
            option.widget,
        )

    def sizeHint(
        self,
        option,
        index,
    ):
        return option.rect.size()


class BookmarkArtworkTableModel(QAbstractTableModel):
    HEADERS = [
        "선택",
        "작품명",
        "작품 ID",
        "작가명",
        "작가 ID",
        "페이지",
        "AI",
        "태그",
        "동기화",
        "최근 동기화",
        "로컬",
        "출처",
    ]

    SORT_COLUMNS = {
        1: "text",
        2: "number_text",
        3: "text",
        4: "number_text",
        5: "number",
        6: "number",
        9: "datetime",
    }

    def __init__(self):
        super().__init__()

        self.bookmark_artworks = []
        self.checked_ids = set()

    def rowCount(self, parent=QModelIndex()) -> int:
        return len(self.bookmark_artworks)

    def columnCount(self, parent=QModelIndex()) -> int:
        return len(self.HEADERS)

    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        row = index.row()
        column = index.column()

        if row < 0 or row >= len(self.bookmark_artworks):
            return None

        bookmark_artwork = self.bookmark_artworks[row]

        if role == Qt.CheckStateRole and column == 0:
            bookmark_artwork_id = bookmark_artwork.get("id")

            if bookmark_artwork_id in self.checked_ids:
                return Qt.Checked

            return Qt.Unchecked

        if role == Qt.TextAlignmentRole:
            if column in (1, 3, 7):
                return Qt.AlignLeft | Qt.AlignVCenter

            return Qt.AlignCenter

        if role != Qt.DisplayRole:
            return None

        if column == 0:
            return ""

        if column == 1:
            return self._empty_to_dash(bookmark_artwork.get("title", ""))

        if column == 2:
            return self._empty_to_dash(bookmark_artwork.get("artwork_id", ""))

        if column == 3:
            return self._empty_to_dash(
                bookmark_artwork.get("artist_name", "")
            )

        if column == 4:
            return self._empty_to_dash(bookmark_artwork.get("artist_id", ""))

        if column == 5:
            return str(bookmark_artwork.get("page_count", 0) or 0)

        if column == 6:
            return self._format_ai_generated(bookmark_artwork)

        if column == 7:
            return self._format_tags(bookmark_artwork.get("pixiv_tags", ""))

        if column == 8:
            return self._format_sync_status(bookmark_artwork)

        if column == 9:
            return self._format_datetime(
                bookmark_artwork.get("last_synced_at")
            )

        if column == 10:
            return self._format_local_match(bookmark_artwork)

        if column == 11:
            return self._empty_to_dash(
                bookmark_artwork.get("source_type", "")
            )

        return ""

    def setData(
        self,
        index: QModelIndex,
        value,
        role=Qt.EditRole,
    ) -> bool:
        if not index.isValid():
            return False

        if role != Qt.CheckStateRole:
            return False

        if index.column() != 0:
            return False

        row = index.row()

        if row < 0 or row >= len(self.bookmark_artworks):
            return False

        bookmark_artwork_id = self.bookmark_artworks[row].get("id")

        if bookmark_artwork_id is None:
            return False

        if value == Qt.Checked:
            self.checked_ids.add(bookmark_artwork_id)
        else:
            self.checked_ids.discard(bookmark_artwork_id)

        self.dataChanged.emit(
            index,
            index,
            [Qt.CheckStateRole],
        )

        return True

    def flags(self, index: QModelIndex):
        base_flags = (
            Qt.ItemIsEnabled
            | Qt.ItemIsSelectable
        )

        if index.isValid() and index.column() == 0:
            return base_flags | Qt.ItemIsUserCheckable

        return base_flags

    def headerData(
        self,
        section: int,
        orientation: Qt.Orientation,
        role=Qt.DisplayRole,
    ):
        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Horizontal:
            return self.HEADERS[section]

        return str(section + 1)

    def sort(
        self,
        column: int,
        order: Qt.SortOrder = Qt.AscendingOrder,
    ):
        if column not in self.SORT_COLUMNS:
            return

        reverse = order == Qt.DescendingOrder
        sort_type = self.SORT_COLUMNS[column]

        self.layoutAboutToBeChanged.emit()
        self.bookmark_artworks.sort(
            key=lambda item: self._sort_key(item, column, sort_type),
            reverse=reverse,
        )
        self.layoutChanged.emit()

    def load_bookmark_artworks(
        self,
        bookmark_artworks: list[dict],
    ):
        self.beginResetModel()
        self.bookmark_artworks = bookmark_artworks
        self.checked_ids = {
            item_id
            for item_id in self.checked_ids
            if self._contains_id(item_id)
        }
        self.endResetModel()

    def check_all(self):
        self.checked_ids = {
            bookmark_artwork.get("id")
            for bookmark_artwork in self.bookmark_artworks
            if bookmark_artwork.get("id") is not None
        }
        self._emit_all_check_changed()

    def clear_checks(self):
        self.checked_ids.clear()
        self._emit_all_check_changed()

    def get_checked_ids(self) -> list[int]:
        return [
            int(item_id)
            for item_id in self.checked_ids
        ]

    def get_displayed_ids(self) -> list[int]:
        return [
            int(bookmark_artwork["id"])
            for bookmark_artwork in self.bookmark_artworks
            if bookmark_artwork.get("id") is not None
        ]

    def get_row_item(
        self,
        row: int,
    ):
        if row < 0 or row >= len(self.bookmark_artworks):
            return None

        return self.bookmark_artworks[row]

    def _emit_all_check_changed(self):
        if not self.bookmark_artworks:
            return

        top_left = self.index(0, 0)
        bottom_right = self.index(len(self.bookmark_artworks) - 1, 0)

        self.dataChanged.emit(
            top_left,
            bottom_right,
            [Qt.CheckStateRole],
        )

    def _contains_id(
        self,
        item_id,
    ) -> bool:
        return any(
            bookmark_artwork.get("id") == item_id
            for bookmark_artwork in self.bookmark_artworks
        )

    def _sort_key(
        self,
        item: dict,
        column: int,
        sort_type: str,
    ):
        if column == 1:
            return str(item.get("title", "") or "").lower()

        if column == 2:
            return self._to_int(item.get("artwork_id"))

        if column == 3:
            return str(item.get("artist_name", "") or "").lower()

        if column == 4:
            return self._to_int(item.get("artist_id"))

        if column == 5:
            return self._to_int(item.get("page_count"))

        if column == 6:
            return self._to_int(item.get("is_ai_generated"))

        if column == 9:
            return self._to_datetime(item.get("last_synced_at"))

        return 0

    def _format_ai_generated(
        self,
        bookmark_artwork: dict,
    ) -> str:
        if int(bookmark_artwork.get("is_ai_generated", 0) or 0):
            return "AI"

        return "일반"

    def _format_tags(
        self,
        value,
    ) -> str:
        text = str(value or "").strip()

        if not text:
            return "-"

        try:
            tags = json.loads(text)
        except json.JSONDecodeError:
            return text

        if not isinstance(tags, list):
            return text

        names = []

        for tag in tags:
            if not isinstance(tag, dict):
                continue

            original = str(tag.get("original", "") or "").strip()

            if original:
                names.append(original)

        if not names:
            return "-"

        return ", ".join(names)

    def _format_sync_status(
        self,
        bookmark_artwork: dict,
    ) -> str:
        status = str(bookmark_artwork.get("sync_status", "") or "pending")
        label = SYNC_STATUS_LABELS.get(status, status)

        retry_count = int(bookmark_artwork.get("sync_retry_count", 0) or 0)

        if status == "failed" and retry_count > 0:
            return f"{label}({retry_count})"

        return label

    def _format_datetime(
        self,
        value,
    ) -> str:
        text = str(value or "").strip()

        if not text:
            return "-"

        return text.replace("T", " ")[:16]

    def _format_local_match(
        self,
        bookmark_artwork: dict,
    ) -> str:
        if bookmark_artwork.get("is_local_artist"):
            return "등록"

        return "미등록"

    def _empty_to_dash(
        self,
        value,
    ) -> str:
        text = str(value or "").strip()

        if not text:
            return "-"

        return text

    def _to_int(
        self,
        value,
    ) -> int:
        try:
            return int(value)
        except (TypeError, ValueError):
            return -1

    def _to_datetime(
        self,
        value,
    ) -> datetime:
        text = str(value or "").strip()

        if not text:
            return datetime.min

        try:
            return datetime.fromisoformat(text)
        except ValueError:
            return datetime.min


class BookmarkArtworkTable(QTableView):
    def __init__(self):
        super().__init__()

        self.model_data = BookmarkArtworkTableModel()

        self._setup_ui()
        self.doubleClicked.connect(self._handle_double_clicked)

    def _setup_ui(self):
        self.setModel(self.model_data)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setAlternatingRowColors(True)
        self.setSortingEnabled(True)
        self.setItemDelegateForColumn(0, CenterCheckBoxDelegate(self))

        vertical_header = self.verticalHeader()
        vertical_header.setVisible(False)
        vertical_header.setDefaultSectionSize(24)

        header = self.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionsClickable(True)
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Interactive)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        header.setSectionResizeMode(3, QHeaderView.Interactive)
        header.setSectionResizeMode(4, QHeaderView.Fixed)
        header.setSectionResizeMode(5, QHeaderView.Fixed)
        header.setSectionResizeMode(6, QHeaderView.Fixed)
        header.setSectionResizeMode(7, QHeaderView.Stretch)
        header.setSectionResizeMode(8, QHeaderView.Fixed)
        header.setSectionResizeMode(9, QHeaderView.Fixed)
        header.setSectionResizeMode(10, QHeaderView.Fixed)
        header.setSectionResizeMode(11, QHeaderView.Fixed)

        self.setColumnWidth(0, 36)
        self.setColumnWidth(1, 300)
        self.setColumnWidth(2, 110)
        self.setColumnWidth(3, 150)
        self.setColumnWidth(4, 110)
        self.setColumnWidth(5, 70)
        self.setColumnWidth(6, 60)
        self.setColumnWidth(7, 400)
        self.setColumnWidth(8, 80)
        self.setColumnWidth(9, 130)
        self.setColumnWidth(10, 80)
        self.setColumnWidth(11, 80)

    def mousePressEvent(
        self,
        event,
    ):
        index = self.indexAt(event.position().toPoint())

        if index.isValid() and index.column() == 0:
            current_state = self.model_data.data(index, Qt.CheckStateRole)

            if current_state == Qt.Checked:
                new_state = Qt.Unchecked
            else:
                new_state = Qt.Checked

            self.model_data.setData(index, new_state, Qt.CheckStateRole)
            return

        super().mousePressEvent(event)

    def load_bookmark_artworks(
        self,
        bookmark_artworks: list[dict],
    ):
        self.model_data.load_bookmark_artworks(bookmark_artworks)

    def check_all(self):
        self.model_data.check_all()

    def clear_checks(self):
        self.model_data.clear_checks()

    def get_checked_ids(self) -> list[int]:
        checked_ids = self.model_data.get_checked_ids()

        if checked_ids:
            return checked_ids

        return self._get_selected_ids()

    def get_displayed_ids(self) -> list[int]:
        return self.model_data.get_displayed_ids()

    def open_selected_pixiv(self):
        selected_rows = self.selectionModel().selectedRows()

        if not selected_rows:
            return

        row = selected_rows[0].row()
        bookmark_artwork = self.model_data.get_row_item(row)

        if bookmark_artwork is None:
            return

        self._open_pixiv(bookmark_artwork)

    def _get_selected_ids(self) -> list[int]:
        ids = []

        for index in self.selectionModel().selectedRows():
            bookmark_artwork = self.model_data.get_row_item(index.row())

            if bookmark_artwork is None:
                continue

            bookmark_artwork_id = bookmark_artwork.get("id")

            if bookmark_artwork_id is None:
                continue

            ids.append(int(bookmark_artwork_id))

        return ids

    def _handle_double_clicked(
        self,
        index: QModelIndex,
    ):
        bookmark_artwork = self.model_data.get_row_item(index.row())

        if bookmark_artwork is None:
            return

        self._open_pixiv(bookmark_artwork)

    def _open_pixiv(
        self,
        bookmark_artwork: dict,
    ):
        artwork_id = str(bookmark_artwork.get("artwork_id", "") or "")

        if not artwork_id:
            return

        webbrowser.open(f"https://www.pixiv.net/artworks/{artwork_id}")
