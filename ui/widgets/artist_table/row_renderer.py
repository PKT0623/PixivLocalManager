from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QTableWidgetItem

from .cell_widgets import (
    create_favorite_button,
    create_shortcut_buttons,
    create_status_badge,
)
from .columns import (
    COLUMN_ARTIST_NAME,
    COLUMN_ARTWORK_COUNT,
    COLUMN_CREATED_AT,
    COLUMN_FAVORITE,
    COLUMN_FILE_COUNT,
    COLUMN_LAST_VIEWED_AT,
    COLUMN_MEMO,
    COLUMN_NO,
    COLUMN_PIXIV_ID,
    COLUMN_RATING,
    COLUMN_SHORTCUTS,
    COLUMN_STATUS,
    COLUMN_TAGS,
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

        is_hidden = bool(artist.get("is_hidden", 0))

        self.set_item(
            row,
            COLUMN_NO,
            index,
            is_hidden,
        )

        self.set_favorite_button(
            row,
            artist.get("id"),
            artist.get("is_favorite", 0),
        )

        self.set_item(
            row,
            COLUMN_ARTIST_NAME,
            artist.get("artist_name"),
            is_hidden,
        )
        self.set_item(
            row,
            COLUMN_PIXIV_ID,
            artist.get("pixiv_id"),
            is_hidden,
        )
        self.set_item(
            row,
            COLUMN_ARTWORK_COUNT,
            artist.get("folder_artwork_count", 0),
            is_hidden,
        )
        self.set_item(
            row,
            COLUMN_FILE_COUNT,
            artist.get("folder_file_count", 0),
            is_hidden,
        )

        self.set_status_badge(
            row,
            artist.get("update_status"),
        )

        self.set_item(
            row,
            COLUMN_RATING,
            artist.get("rating", 0),
            is_hidden,
        )
        self.set_item(
            row,
            COLUMN_TAGS,
            artist.get("artist_tags", ""),
            is_hidden,
        )
        self.set_item(
            row,
            COLUMN_LAST_VIEWED_AT,
            artist.get("last_viewed_at"),
            is_hidden,
        )
        self.set_item(
            row,
            COLUMN_CREATED_AT,
            artist.get("created_at"),
            is_hidden,
        )
        self.set_item(
            row,
            COLUMN_MEMO,
            artist.get("memo"),
            is_hidden,
        )

        self.set_shortcut_buttons(
            row,
            artist.get("folder_path"),
            artist.get("pixiv_id"),
        )

    def set_item(
        self,
        row: int,
        column: int,
        value,
        is_hidden: bool = False,
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
            COLUMN_PIXIV_ID,
            COLUMN_ARTWORK_COUNT,
            COLUMN_FILE_COUNT,
            COLUMN_RATING,
            COLUMN_LAST_VIEWED_AT,
            COLUMN_CREATED_AT,
        ):
            item.setTextAlignment(Qt.AlignCenter)

        if is_hidden:
            self.apply_hidden_style(item)

        self.table.setItem(row, column, item)

    def apply_hidden_style(self, item: QTableWidgetItem):
        item.setBackground(QColor("#e3e3e3"))
        item.setForeground(QColor("#777777"))

    def set_favorite_button(
        self,
        row: int,
        artist_id,
        is_favorite,
    ):
        widget = create_favorite_button(
            artist_id,
            bool(is_favorite),
            self.table.favorite_toggled.emit,
        )

        self.table.setCellWidget(
            row,
            COLUMN_FAVORITE,
            widget,
        )

    def set_status_badge(
        self,
        row: int,
        status,
    ):
        badge = create_status_badge(status)

        self.table.setCellWidget(row, COLUMN_STATUS, badge)
        self.table.setRowHeight(row, 42)

    def set_shortcut_buttons(
        self,
        row: int,
        folder_path,
        pixiv_id,
    ):
        widget = create_shortcut_buttons(
            folder_path,
            pixiv_id,
            self.table.actions.open_folder,
            self.table.actions.open_pixiv_page,
        )

        self.table.setCellWidget(
            row,
            COLUMN_SHORTCUTS,
            widget,
        )
