from dataclasses import dataclass


@dataclass
class PixivUserMetadata:
    pixiv_user_id: str
    user_name: str
    artwork_count: int
    pixiv_tags: str


@dataclass
class PixivArtworkMetadata:
    artwork_id: str
    title: str
    artist_id: str
    artist_name: str
    page_count: int
    ai_type: int
    is_ai_generated: bool
    pixiv_tags: str
