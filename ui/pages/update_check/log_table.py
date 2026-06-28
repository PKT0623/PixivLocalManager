from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QTableWidget,
)

from .log_table_parts import (
    LOG_TABLE_HEADERS,
    UpdateLogTableFormatterMixin,
    UpdateLogTableRowActionsMixin,
    UpdateLogTableSelectionActionsMixin,
)


class UpdateLogTable(
    QTableWidget,
    UpdateLogTableRowActionsMixin,
    UpdateLogTableSelectionActionsMixin,
    UpdateLogTableFormatterMixin,
):
    artist_detail_requested = Signal(int)
    selection_changed = Signal()

    HEADERS = LOG_TABLE_HEADERS

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
