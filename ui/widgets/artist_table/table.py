from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QTableWidget,
)

from .actions import ArtistTableActions
from .columns import (
    COLUMN_ARTIST_NAME,
    COLUMN_ARTWORK_COUNT,
    COLUMN_FAVORITE,
    COLUMN_FILE_COUNT,
    COLUMN_FOLDER_SIZE,
    COLUMN_HEADERS,
    COLUMN_LAST_VIEWED_AT,
    COLUMN_MISSING_ARTWORK_COUNT,
    COLUMN_NO,
    COLUMN_PIXIV_ID,
    COLUMN_RATING,
    COLUMN_SHORTCUTS,
    COLUMN_SORT_FIELDS,
    COLUMN_STATUS,
    COLUMN_TAGS,
    COLUMN_UPDATED_AT,
    COLUMNS,
)
from .row_renderer import ArtistTableRowRenderer


class ArtistTable(QTableWidget):
    artist_selected = Signal(int)
    sort_requested = Signal(str, bool)
    favorite_toggled = Signal(int)
    rating_changed = Signal(int, int)
    context_rating_requested = Signal(list)
    context_favorite_requested = Signal(list, bool)
    context_delete_requested = Signal(list)
    folder_open_failed = Signal(str)

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
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setAlternatingRowColors(True)
        self.setSortingEnabled(False)
        self.setContextMenuPolicy(Qt.CustomContextMenu)

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
        self.customContextMenuRequested.connect(
            self.actions.show_context_menu
        )

    def _setup_header_resize_modes(self, header):
        fixed_columns = (
            COLUMN_NO,
            COLUMN_FAVORITE,
            COLUMN_ARTIST_NAME,
            COLUMN_PIXIV_ID,
            COLUMN_ARTWORK_COUNT,
            COLUMN_MISSING_ARTWORK_COUNT,
            COLUMN_FILE_COUNT,
            COLUMN_FOLDER_SIZE,
            COLUMN_STATUS,
            COLUMN_RATING,
            COLUMN_LAST_VIEWED_AT,
            COLUMN_UPDATED_AT,
            COLUMN_SHORTCUTS,
        )

        stretch_columns = (
            COLUMN_TAGS,
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

        self.setColumnWidth(
            COLUMN_ARTIST_NAME,
            150,
        )

    def set_artists(self, artists: list[dict]):
        self.artists = artists
        self.artist_ids = [
            artist.get("id")
            for artist in artists
        ]

        self.setUpdatesEnabled(False)

        try:
            self.setRowCount(0)
            self.setRowCount(len(artists))

            for index, artist in enumerate(
                artists,
                start=1,
            ):
                row = index - 1

                self.row_renderer.render_artist_row(
                    row,
                    index,
                    artist,
                )
        finally:
            self.setUpdatesEnabled(True)

    def get_selected_artist_ids(self) -> list[int]:
        selected_rows = {
            index.row()
            for index in self.selectionModel().selectedRows()
        }

        artist_ids = []

        for row in sorted(selected_rows):
            if row < 0 or row >= len(self.artist_ids):
                continue

            artist_id = self.artist_ids[row]

            if artist_id is None:
                continue

            artist_ids.append(int(artist_id))

        return artist_ids

    def select_artist_ids(self, artist_ids: list[int]):
        target_ids = {
            int(artist_id)
            for artist_id in artist_ids
        }

        self.clearSelection()

        selection_model = self.selectionModel()
        first_index = None

        for row, artist_id in enumerate(self.artist_ids):
            if artist_id is None:
                continue

            if int(artist_id) not in target_ids:
                continue

            index = self.model().index(row, 0)

            selection_model.select(
                index,
                selection_model.SelectionFlag.Select
                | selection_model.SelectionFlag.Rows,
            )

            if first_index is None:
                first_index = index

        if first_index is not None:
            self.setCurrentIndex(first_index)
            self.scrollTo(first_index)

    def set_sort_indicators(
        self,
        sort_rules: list[tuple[str, bool]],
    ):
        headers = []

        for column in COLUMNS:
            header = column.header
            sort_field = COLUMN_SORT_FIELDS.get(column.index)

            if sort_field is not None:
                sort_rule_index = self._find_sort_rule_index(
                    sort_rules,
                    sort_field,
                )

                if sort_rule_index is not None:
                    _, sort_reverse = sort_rules[sort_rule_index]
                    header += " ▼" if sort_reverse else " ▲"

                    if len(sort_rules) > 1:
                        header += f"({sort_rule_index + 1})"

            headers.append(header)

        self.setHorizontalHeaderLabels(headers)

    def _find_sort_rule_index(
        self,
        sort_rules: list[tuple[str, bool]],
        sort_field: str,
    ) -> int | None:
        for index, rule in enumerate(sort_rules):
            if rule[0] == sort_field:
                return index

        return None

    def set_rating_display_mode(self, mode: str):
        if mode not in ("stars", "number"):
            return

        self.rating_display_mode = mode
        self.set_artists(self.artists)
