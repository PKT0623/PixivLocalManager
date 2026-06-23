from dataclasses import dataclass


@dataclass
class PixivArtworkFetchResult:
    pixiv_id: str
    artwork_ids: list[str]
    artwork_ids_text: str
