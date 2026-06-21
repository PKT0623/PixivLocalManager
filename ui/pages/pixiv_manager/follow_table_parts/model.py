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


class FollowUserTableModel(PixivManagerBaseTableModel):
    HEADERS = HEADERS
    SORT_COLUMNS = SORT_COLUMNS
    ITEM_ID_FIELD = "id"

    def load_follow_users(
        self,
        follow_users: list[dict],
    ):
        self.load_items(follow_users)

    def get_display_value(
        self,
        item: dict,
        column: int,
    ) -> str:
        if column == 1:
            return empty_to_dash(item.get("user_name", ""))

        if column == 2:
            return empty_to_dash(item.get("pixiv_user_id", ""))

        if column == 3:
            return str(item.get("artwork_count", 0) or 0)

        if column == 4:
            return format_tags(
                item.get("pixiv_tags", ""),
                prefer_translated=True,
            )

        if column == 5:
            return format_sync_status(item)

        if column == 6:
            return format_datetime(item.get("last_synced_at"))

        if column == 7:
            return format_local_match(item)

        if column == 8:
            return empty_to_dash(item.get("source_type", ""))

        return ""

    def get_sort_key(
        self,
        item: dict,
        column: int,
        sort_type: str,
    ):
        if column == 1:
            return str(item.get("user_name", "") or "").lower()

        if column == 2:
            return to_int(item.get("pixiv_user_id"))

        if column == 3:
            return to_int(item.get("artwork_count"))

        if column == 6:
            return to_datetime(item.get("last_synced_at"))

        return 0

    def get_alignment(
        self,
        column: int,
    ):
        if column in (1, 4):
            return Qt.AlignLeft | Qt.AlignVCenter

        return Qt.AlignCenter
