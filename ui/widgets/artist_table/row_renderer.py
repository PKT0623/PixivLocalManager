from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTableWidgetItem

from .cell_widgets import (
    create_favorite_button,
    create_shortcut_buttons,
    create_status_badge,
)
from .columns import (
    COLUMN_ARTIST_NAME,
    COLUMN_ARTWORK_COUNT,
    COLUMN_FAVORITE,
    COLUMN_FILE_COUNT,
    COLUMN_FOLDER_SIZE,
    COLUMN_LAST_VIEWED_AT,
    COLUMN_MISSING_ARTWORK_COUNT,
    COLUMN_NO,
    COLUMN_PIXIV_ID,
    COLUMN_RATING,
    COLUMN_SHORTCUTS,
    COLUMN_STATUS,
    COLUMN_TAGS,
    COLUMN_UPDATED_AT,
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

        self.set_item(
            row,
            COLUMN_NO,
            index,
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
        )
        self.set_item(
            row,
            COLUMN_PIXIV_ID,
            artist.get("pixiv_id"),
        )
        self.set_item(
            row,
            COLUMN_ARTWORK_COUNT,
            artist.get("folder_artwork_count", 0),
        )
        self.set_item(
            row,
            COLUMN_MISSING_ARTWORK_COUNT,
            self.get_missing_artwork_count(artist),
        )
        self.set_item(
            row,
            COLUMN_FILE_COUNT,
            artist.get("folder_file_count", 0),
        )
        self.set_item(
            row,
            COLUMN_FOLDER_SIZE,
            artist.get("folder_size_bytes", 0),
        )

        self.set_status_badge(
            row,
            artist.get("update_status"),
        )

        self.set_item(
            row,
            COLUMN_RATING,
            artist.get("rating", 0),
        )
        self.set_item(
            row,
            COLUMN_TAGS,
            artist.get("artist_tags", ""),
        )
        self.set_item(
            row,
            COLUMN_LAST_VIEWED_AT,
            artist.get("last_viewed_at"),
        )
        self.set_item(
            row,
            COLUMN_UPDATED_AT,
            artist.get("updated_at"),
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
            COLUMN_MISSING_ARTWORK_COUNT,
            COLUMN_FILE_COUNT,
            COLUMN_FOLDER_SIZE,
            COLUMN_RATING,
            COLUMN_LAST_VIEWED_AT,
            COLUMN_UPDATED_AT,
        ):
            item.setTextAlignment(Qt.AlignCenter)

        self.table.setItem(row, column, item)

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

    def get_missing_artwork_count(self, artist: dict) -> int:
        local_ids = self.parse_artwork_ids(
            artist.get("local_latest_artwork_ids", "")
        )
        pixiv_ids = self.parse_artwork_ids(
            artist.get("pixiv_latest_artwork_ids", "")
        )

        if not pixiv_ids:
            return 0

        return len(pixiv_ids - local_ids)

    def parse_artwork_ids(self, value) -> set[str]:
        if not value:
            return set()

        if isinstance(value, (list, tuple, set)):
            return {
                str(item).strip()
                for item in value
                if str(item).strip()
            }

        text = str(value)

        return {
            item.strip()
            for item in text.replace("\n", ",").split(",")
            if item.strip()
        }
