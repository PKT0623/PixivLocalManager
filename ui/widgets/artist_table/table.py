from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QTableWidget,
)

from .actions import ArtistTableActions
from .columns import (
    COLUMN_NO,
    COLUMN_ARTIST_NAME,
    COLUMN_ARTWORK_COUNT,
    COLUMN_FAVORITE,
    COLUMN_FILE_COUNT,
    COLUMN_HEADERS,
    COLUMN_LAST_VIEWED_AT,
    COLUMN_MEMO,
    COLUMN_SHORTCUTS,
    COLUMN_PIXIV_ID,
    COLUMN_RATING,
    COLUMN_STATUS,
    COLUMN_TAGS,
    COLUMNS,
)
from .row_renderer import ArtistTableRowRenderer


class ArtistTable(QTableWidget):
    artist_selected = Signal(int)
    sort_requested = Signal(str)
    favorite_toggled = Signal(int)

    def __init__(self):
        super().__init__()

        self.artist_ids = []
        self.artists = []
        self.rating_display_mode = "stars"
        self.shortcut_column = COLUMN_SHORTCUTS

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
        self.verticalHeader().setDefaultSectionSize(42)

        header = self.horizontalHeader()
        header.setSectionsClickable(True)
        header.sectionClicked.connect(
            self.actions.handle_header_clicked
        )

        self._setup_header_resize_modes(header)

        self.cellClicked.connect(
            self.actions.handle_cell_clicked
        )
        self.cellDoubleClicked.connect(
            self.actions.handle_cell_double_clicked
        )

    def _setup_header_resize_modes(self, header):
        fixed_columns = (
            COLUMN_NO,
            COLUMN_FAVORITE,
            COLUMN_PIXIV_ID,
            COLUMN_ARTWORK_COUNT,
            COLUMN_FILE_COUNT,
            COLUMN_STATUS,
            COLUMN_RATING,
            COLUMN_LAST_VIEWED_AT,
            COLUMN_SHORTCUTS,
        )

        stretch_columns = (
            COLUMN_ARTIST_NAME,
            COLUMN_TAGS,
            COLUMN_MEMO,
        )

        for column in COLUMNS:
            if column.index in fixed_columns:
                header.setSectionResizeMode(
                    column.index,
                    QHeaderView.Fixed,
                )
            elif column.index in stretch_columns:
                header.setSectionResizeMode(
                    column.index,
                    QHeaderView.Stretch,
                )
            elif column.width is not None:
                header.setSectionResizeMode(
                    column.index,
                    QHeaderView.ResizeToContents,
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
