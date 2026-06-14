from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QTableWidget,
)

from .actions import ArtistTableActions
from .columns import (
    COLUMN_HEADERS,
    COLUMN_PIXIV_BUTTON,
    COLUMN_STATUS,
    COLUMN_RATING,
    COLUMNS,
)
from .row_renderer import ArtistTableRowRenderer


class ArtistTable(QTableWidget):
    artist_selected = Signal(int)
    sort_requested = Signal(str)

    def __init__(self):
        super().__init__()

        self.artist_ids = []
        self.artists = []
        self.rating_display_mode = "stars"
        self.pixiv_button_column = COLUMN_PIXIV_BUTTON

        self.actions = ArtistTableActions(self)
        self.row_renderer = ArtistTableRowRenderer(self)

        self._setup_ui()

    def _setup_ui(self):
        self.setColumnCount(len(COLUMNS))
        self.setHorizontalHeaderLabels(COLUMN_HEADERS)

        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setAlternatingRowColors(True)
        self.setSortingEnabled(False)

        self.verticalHeader().setVisible(False)
        self.verticalHeader().setDefaultSectionSize(32)

        header = self.horizontalHeader()
        header.setSectionsClickable(True)
        header.sectionClicked.connect(
            self.actions.handle_header_clicked
        )

        self._setup_header_resize_modes(header)

        self.cellDoubleClicked.connect(
            self.actions.handle_cell_double_clicked
        )

    def _setup_header_resize_modes(self, header):
        for column in COLUMNS:
            if column.index in (COLUMN_STATUS, COLUMN_RATING):
                header.setSectionResizeMode(
                    column.index,
                    QHeaderView.Fixed,
                )
            elif column.width is not None:
                header.setSectionResizeMode(
                    column.index,
                    QHeaderView.ResizeToContents,
                )
            elif column.index in (1, 6):
                header.setSectionResizeMode(
                    column.index,
                    QHeaderView.Stretch,
                )
            else:
                header.setSectionResizeMode(
                    column.index,
                    QHeaderView.ResizeToContents,
                )

            if column.width is not None:
                self.setColumnWidth(
                    column.index,
                    column.width,
                )

    def set_artists(self, artists: list[dict]):
        self.artists = artists
        self.artist_ids = []

        self.setRowCount(0)

        for index, artist in enumerate(
            artists,
            start=1,
        ):
            row = self.rowCount()
            self.insertRow(row)

            self.row_renderer.render_artist_row(
                row,
                index,
                artist,
            )

    def set_rating_display_mode(self, mode: str):
        if mode not in ("stars", "number"):
            return

        self.rating_display_mode = mode
        self.set_artists(self.artists)
