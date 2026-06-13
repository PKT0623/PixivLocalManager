from dataclasses import dataclass
from datetime import datetime


@dataclass
class Artist:
    id: int | None = None

    artist_name: str = ""
    pixiv_id: int = 0

    folder_path: str = ""

    rating: int = 0
    status: str = "normal"

    memo: str = ""

    local_latest_artwork_id: str = ""
    pixiv_latest_artwork_id: str = ""

    update_status: str = "unknown"

    last_checked_at: datetime | None = None

    created_at: datetime | None = None
    updated_at: datetime | None = None
