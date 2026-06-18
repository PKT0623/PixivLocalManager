from dataclasses import dataclass
from datetime import datetime


@dataclass
class BookmarkArtwork:
    id: int | None = None

    artwork_id: str = ""
    title: str = ""

    artist_id: str = ""
    artist_name: str = ""

    bookmark_count: int = 0
    page_count: int = 0

    ai_type: int = 0
    is_ai_generated: bool = False

    pixiv_tags: str = ""

    local_artist_id: int | None = None
    is_local_artist: bool = False

    is_favorite: bool = False
    is_hidden: bool = False

    memo: str = ""

    source_type: str = "manual"

    last_synced_at: datetime | None = None
    sync_status: str = "pending"
    sync_error_message: str = ""
    sync_retry_count: int = 0

    created_at: datetime | None = None
    updated_at: datetime | None = None
