from dataclasses import dataclass
from datetime import datetime


@dataclass
class Artist:
    id: int | None = None

    artist_name: str = ""
    pixiv_id: str = ""

    folder_path: str = ""
    folder_size_bytes: int = 0
    folder_file_count: int = 0
    folder_artwork_count: int = 0

    rating: int = 0
    status: str = "normal"

    is_favorite: bool = False
    is_hidden: bool = False
    artist_tags: str = ""

    memo: str = ""

    local_latest_artwork_ids: str = ""
    pixiv_latest_artwork_ids: str = ""

    update_status: str = "unknown"

    last_checked_at: datetime | None = None
    last_viewed_at: datetime | None = None

    created_at: datetime | None = None
    updated_at: datetime | None = None
