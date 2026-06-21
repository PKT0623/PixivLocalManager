from app.services.bookmark import BookmarkService
from app.services.follow import FollowService
from app.services.pixiv.metadata_service import PixivMetadataService
from app.services.pixiv.sync_parts import (
    BookmarkSyncMixin,
    FollowSyncMixin,
    PixivSyncHelperMixin,
    PixivSyncStatus,
)
from app.services.tag import TagService


class PixivSyncService(
    FollowSyncMixin,
    BookmarkSyncMixin,
    PixivSyncHelperMixin,
):
    def __init__(
        self,
        metadata_service: PixivMetadataService | None = None,
    ):
        self.metadata_service = metadata_service or PixivMetadataService()
        self.follow_service = FollowService()
        self.bookmark_service = BookmarkService()
        self.tag_service = TagService()


__all__ = [
    "PixivSyncService",
    "PixivSyncStatus",
]
