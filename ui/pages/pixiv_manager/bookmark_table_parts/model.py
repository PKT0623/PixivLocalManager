from PySide6.QtCore import Qt

from ..table_common import (
    PixivManagerBaseTableModel,
    empty_to_dash,
    format_datetime,
    format_local_match,
    format_sync_status,
    format_tags,
    to_datetime,
    to_int,
)
from .constants import HEADERS, SORT_COLUMNS


class BookmarkArtworkTableModel(PixivManagerBaseTableModel):
    HEADERS = HEADERS
    SORT_COLUMNS = SORT_COLUMNS
    ITEM_ID_FIELD = "id"

    def load_bookmark_artworks(
        self,
        bookmark_artworks: list[dict],
    ):
        self.load_items(bookmark_artworks)

    def get_display_value(
        self,
        item: dict,
        column: int,
    ) -> str:
        if column == 1:
            return empty_to_dash(item.get("title", ""))

        if column == 2:
            return empty_to_dash(item.get("artwork_id", ""))

        if column == 3:
            return empty_to_dash(item.get("artist_name", ""))

        if column == 4:
            return empty_to_dash(item.get("artist_id", ""))

        if column == 5:
            return str(item.get("page_count", 0) or 0)

        if column == 6:
            return self._format_ai_generated(item)

        if column == 7:
            return format_tags(item.get("pixiv_tags", ""))

        if column == 8:
            return format_sync_status(item)

        if column == 9:
            return format_datetime(item.get("last_synced_at"))

        if column == 10:
            return format_local_match(item)

        if column == 11:
            return empty_to_dash(item.get("source_type", ""))

        return ""

    def get_sort_key(
        self,
        item: dict,
        column: int,
        sort_type: str,
    ):
        if column == 1:
            return str(item.get("title", "") or "").lower()

        if column == 2:
            return to_int(item.get("artwork_id"))

        if column == 3:
            return str(item.get("artist_name", "") or "").lower()

        if column == 4:
            return to_int(item.get("artist_id"))

        if column == 5:
            return to_int(item.get("page_count"))

        if column == 6:
            return to_int(item.get("is_ai_generated"))

        if column == 9:
            return to_datetime(item.get("last_synced_at"))

        return 0

    def get_alignment(
        self,
        column: int,
    ):
        if column in (1, 3, 7):
            return Qt.AlignLeft | Qt.AlignVCenter

        return Qt.AlignCenter

    def _format_ai_generated(
        self,
        bookmark_artwork: dict,
    ) -> str:
        if int(bookmark_artwork.get("is_ai_generated", 0) or 0):
            return "AI"

        return "일반"
