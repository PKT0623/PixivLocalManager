from dataclasses import dataclass
from datetime import datetime


@dataclass
class FollowUser:
    id: int | None = None

    pixiv_user_id: str = ""
    user_name: str = ""

    profile_image_url: str = ""
    comment: str = ""

    artwork_count: int = 0
    file_count: int = 0

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
