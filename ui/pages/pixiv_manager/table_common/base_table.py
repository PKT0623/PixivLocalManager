from PySide6.QtCore import QModelIndex, Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QTableView,
)


class PixivManagerBaseTable(QTableView):
    PIXIV_URL_TEMPLATE = ""

    def _setup_base_ui(self):
        self.setModel(self.model_data)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setAlternatingRowColors(True)
        self.setSortingEnabled(True)

        vertical_header = self.verticalHeader()
        vertical_header.setVisible(False)
        vertical_header.setDefaultSectionSize(24)

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
        item = self.model_data.get_row_item(row)

        if item is None:
            return

        self._open_pixiv(item)

    def _get_selected_ids(self) -> list[int]:
        ids = []

        for index in self.selectionModel().selectedRows():
            item = self.model_data.get_row_item(index.row())

            if item is None:
                continue

            item_id = item.get("id")

            if item_id is None:
                continue

            ids.append(int(item_id))

        return ids

    def _handle_double_clicked(
        self,
        index: QModelIndex,
    ):
        item = self.model_data.get_row_item(index.row())

        if item is None:
            return

        self._open_pixiv(item)

    def _open_pixiv(
        self,
        item: dict,
    ):
        raise NotImplementedError
