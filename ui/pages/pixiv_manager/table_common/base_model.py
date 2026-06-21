from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt


class PixivManagerBaseTableModel(QAbstractTableModel):
    HEADERS = []
    SORT_COLUMNS = {}
    ITEM_ID_FIELD = "id"

    def __init__(self):
        super().__init__()

        self.items = []
        self.checked_ids = set()

    def rowCount(self, parent=QModelIndex()) -> int:
        return len(self.items)

    def columnCount(self, parent=QModelIndex()) -> int:
        return len(self.HEADERS)

    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        row = index.row()
        column = index.column()

        if row < 0 or row >= len(self.items):
            return None

        item = self.items[row]

        if role == Qt.CheckStateRole and column == 0:
            item_id = item.get(self.ITEM_ID_FIELD)

            if item_id in self.checked_ids:
                return Qt.Checked

            return Qt.Unchecked

        if role == Qt.TextAlignmentRole:
            return self.get_alignment(column)

        if role != Qt.DisplayRole:
            return None

        if column == 0:
            return ""

        return self.get_display_value(item, column)

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

        if row < 0 or row >= len(self.items):
            return False

        item_id = self.items[row].get(self.ITEM_ID_FIELD)

        if item_id is None:
            return False

        if value == Qt.Checked:
            self.checked_ids.add(item_id)
        else:
            self.checked_ids.discard(item_id)

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
        self.items.sort(
            key=lambda item: self.get_sort_key(item, column, sort_type),
            reverse=reverse,
        )
        self.layoutChanged.emit()

    def load_items(
        self,
        items: list[dict],
    ):
        self.beginResetModel()
        self.items = items
        self.checked_ids = {
            item_id
            for item_id in self.checked_ids
            if self._contains_id(item_id)
        }
        self.endResetModel()

    def check_all(self):
        self.checked_ids = {
            item.get(self.ITEM_ID_FIELD)
            for item in self.items
            if item.get(self.ITEM_ID_FIELD) is not None
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
            int(item[self.ITEM_ID_FIELD])
            for item in self.items
            if item.get(self.ITEM_ID_FIELD) is not None
        ]

    def get_row_item(
        self,
        row: int,
    ):
        if row < 0 or row >= len(self.items):
            return None

        return self.items[row]

    def get_display_value(
        self,
        item: dict,
        column: int,
    ) -> str:
        raise NotImplementedError

    def get_sort_key(
        self,
        item: dict,
        column: int,
        sort_type: str,
    ):
        raise NotImplementedError

    def get_alignment(
        self,
        column: int,
    ):
        return Qt.AlignCenter

    def _emit_all_check_changed(self):
        if not self.items:
            return

        top_left = self.index(0, 0)
        bottom_right = self.index(len(self.items) - 1, 0)

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
            item.get(self.ITEM_ID_FIELD) == item_id
            for item in self.items
        )
