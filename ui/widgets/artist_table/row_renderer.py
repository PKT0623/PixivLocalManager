from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTableWidgetItem

from .cell_widgets import create_pixiv_button, create_status_badge
from .columns import (
    COLUMN_ARTIST_NAME,
    COLUMN_ARTWORK_COUNT,
    COLUMN_MEMO,
    COLUMN_NO,
    COLUMN_PIXIV_BUTTON,
    COLUMN_PIXIV_ID,
    COLUMN_RATING,
    COLUMN_STATUS,
)
from .formatters import format_cell_value


class ArtistTableRowRenderer:
    def __init__(self, table):
        self.table = table

    def render_artist_row(
        self,
        row: int,
        index: int,
        artist: dict,
    ):
        self.table.artist_ids.append(artist.get("id"))

        self.set_item(row, COLUMN_NO, index)
        self.set_item(row, COLUMN_ARTIST_NAME, artist.get("artist_name"))
        self.set_item(row, COLUMN_PIXIV_ID, artist.get("pixiv_id"))
        self.set_item(
            row,
            COLUMN_ARTWORK_COUNT,
            artist.get("folder_artwork_count", 0),
        )

        self.set_status_badge(
            row,
            artist.get("update_status"),
        )

        self.set_item(row, COLUMN_RATING, artist.get("rating", 0))
        self.set_item(row, COLUMN_MEMO, artist.get("memo"))

        self.set_pixiv_button(
            row,
            artist.get("pixiv_id"),
        )

    def set_item(
        self,
        row: int,
        column: int,
        value,
    ):
        text = format_cell_value(
            column,
            value,
            self.table.rating_display_mode,
        )

        item = QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)

        if column in (
            COLUMN_NO,
            COLUMN_ARTWORK_COUNT,
            COLUMN_RATING,
        ):
            item.setTextAlignment(Qt.AlignCenter)

        self.table.setItem(row, column, item)

    def set_status_badge(
        self,
        row: int,
        status,
    ):
        badge = create_status_badge(status)

        self.table.setCellWidget(row, COLUMN_STATUS, badge)
        self.table.setRowHeight(row, 32)

    def set_pixiv_button(
        self,
        row: int,
        pixiv_id,
    ):
        button = create_pixiv_button(
            pixiv_id,
            self.table.actions.open_pixiv_page,
        )

        self.table.setCellWidget(
            row,
            COLUMN_PIXIV_BUTTON,
            button,
        )
