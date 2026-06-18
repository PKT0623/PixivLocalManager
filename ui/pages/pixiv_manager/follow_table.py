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


class FollowUserTableModel(QAbstractTableModel):
    HEADERS = [
        "선택",
        "유저명",
        "Pixiv ID",
        "작품 수",
        "태그",
        "동기화",
        "최근 동기화",
        "로컬",
        "출처",
    ]

    SORT_COLUMNS = {
        1: "text",
        2: "number_text",
        3: "number",
        6: "datetime",
    }

    def __init__(self):
        super().__init__()

        self.follow_users = []
        self.checked_ids = set()

    def rowCount(self, parent=QModelIndex()) -> int:
        return len(self.follow_users)

    def columnCount(self, parent=QModelIndex()) -> int:
        return len(self.HEADERS)

    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        row = index.row()
        column = index.column()

        if row < 0 or row >= len(self.follow_users):
            return None

        follow_user = self.follow_users[row]

        if role == Qt.CheckStateRole and column == 0:
            follow_user_id = follow_user.get("id")

            if follow_user_id in self.checked_ids:
                return Qt.Checked

            return Qt.Unchecked

        if role == Qt.TextAlignmentRole:
            if column in (1, 4):
                return Qt.AlignLeft | Qt.AlignVCenter

            return Qt.AlignCenter

        if role != Qt.DisplayRole:
            return None

        if column == 0:
            return ""

        if column == 1:
            return self._empty_to_dash(follow_user.get("user_name", ""))

        if column == 2:
            return self._empty_to_dash(follow_user.get("pixiv_user_id", ""))

        if column == 3:
            return str(follow_user.get("artwork_count", 0) or 0)

        if column == 4:
            return self._format_tags(follow_user.get("pixiv_tags", ""))

        if column == 5:
            return self._format_sync_status(follow_user)

        if column == 6:
            return self._format_datetime(follow_user.get("last_synced_at"))

        if column == 7:
            return self._format_local_match(follow_user)

        if column == 8:
            return self._empty_to_dash(follow_user.get("source_type", ""))

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

        if row < 0 or row >= len(self.follow_users):
            return False

        follow_user_id = self.follow_users[row].get("id")

        if follow_user_id is None:
            return False

        if value == Qt.Checked:
            self.checked_ids.add(follow_user_id)
        else:
            self.checked_ids.discard(follow_user_id)

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
        self.follow_users.sort(
            key=lambda item: self._sort_key(item, column, sort_type),
            reverse=reverse,
        )
        self.layoutChanged.emit()

    def load_follow_users(
        self,
        follow_users: list[dict],
    ):
        self.beginResetModel()
        self.follow_users = follow_users
        self.checked_ids = {
            item_id
            for item_id in self.checked_ids
            if self._contains_id(item_id)
        }
        self.endResetModel()

    def check_all(self):
        self.checked_ids = {
            follow_user.get("id")
            for follow_user in self.follow_users
            if follow_user.get("id") is not None
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
            int(follow_user["id"])
            for follow_user in self.follow_users
            if follow_user.get("id") is not None
        ]

    def get_row_item(
        self,
        row: int,
    ):
        if row < 0 or row >= len(self.follow_users):
            return None

        return self.follow_users[row]

    def _emit_all_check_changed(self):
        if not self.follow_users:
            return

        top_left = self.index(0, 0)
        bottom_right = self.index(len(self.follow_users) - 1, 0)

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
            follow_user.get("id") == item_id
            for follow_user in self.follow_users
        )

    def _sort_key(
        self,
        item: dict,
        column: int,
        sort_type: str,
    ):
        if column == 1:
            return str(item.get("user_name", "") or "").lower()

        if column == 2:
            return self._to_int(item.get("pixiv_user_id"))

        if column == 3:
            return self._to_int(item.get("artwork_count"))

        if column == 6:
            return self._to_datetime(item.get("last_synced_at"))

        return 0

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

            translated = str(tag.get("translated", "") or "").strip()
            original = str(tag.get("original", "") or "").strip()

            if translated:
                names.append(translated)
            elif original:
                names.append(original)

        if not names:
            return "-"

        return ", ".join(names)

    def _format_sync_status(
        self,
        follow_user: dict,
    ) -> str:
        status = str(follow_user.get("sync_status", "") or "pending")
        label = SYNC_STATUS_LABELS.get(status, status)

        retry_count = int(follow_user.get("sync_retry_count", 0) or 0)

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
        follow_user: dict,
    ) -> str:
        if follow_user.get("is_local_artist"):
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


class FollowUserTable(QTableView):
    def __init__(self):
        super().__init__()

        self.model_data = FollowUserTableModel()

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
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        header.setSectionResizeMode(3, QHeaderView.Fixed)
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        header.setSectionResizeMode(5, QHeaderView.Fixed)
        header.setSectionResizeMode(6, QHeaderView.Fixed)
        header.setSectionResizeMode(7, QHeaderView.Fixed)
        header.setSectionResizeMode(8, QHeaderView.Fixed)

        self.setColumnWidth(0, 36)
        self.setColumnWidth(1, 150)
        self.setColumnWidth(2, 110)
        self.setColumnWidth(3, 80)
        self.setColumnWidth(5, 80)
        self.setColumnWidth(6, 130)
        self.setColumnWidth(7, 80)
        self.setColumnWidth(8, 80)

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

    def load_follow_users(
        self,
        follow_users: list[dict],
    ):
        self.model_data.load_follow_users(follow_users)

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
        follow_user = self.model_data.get_row_item(row)

        if follow_user is None:
            return

        self._open_pixiv(follow_user)

    def _get_selected_ids(self) -> list[int]:
        ids = []

        for index in self.selectionModel().selectedRows():
            follow_user = self.model_data.get_row_item(index.row())

            if follow_user is None:
                continue

            follow_user_id = follow_user.get("id")

            if follow_user_id is None:
                continue

            ids.append(int(follow_user_id))

        return ids

    def _handle_double_clicked(
        self,
        index: QModelIndex,
    ):
        follow_user = self.model_data.get_row_item(index.row())

        if follow_user is None:
            return

        self._open_pixiv(follow_user)

    def _open_pixiv(
        self,
        follow_user: dict,
    ):
        pixiv_user_id = str(follow_user.get("pixiv_user_id", "") or "")

        if not pixiv_user_id:
            return

        webbrowser.open(f"https://www.pixiv.net/users/{pixiv_user_id}")
