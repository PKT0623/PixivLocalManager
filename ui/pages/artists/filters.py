from datetime import datetime

from ui.widgets.artist_table.formatters import parse_artist_tags


DEFAULT_SORT_REVERSE = {
    "artist_name": False,
    "pixiv_id": False,
    "folder_artwork_count": True,
    "missing_artwork_count": True,
    "folder_file_count": True,
    "folder_size_bytes": True,
    "rating": True,
    "last_viewed_at": True,
    "updated_at": True,
}


def filter_artists(
    artists: list[dict],
    keyword: str,
    search_mode: str = "all",
    rating_value: int = 0,
    rating_filter_mode: str = "min",
    favorite_only: bool = False,
    update_required_only: bool = False,
    unknown_only: bool = False,
    unrated_only: bool = False,
) -> list[dict]:
    keyword = keyword.strip().lower()

    filtered = []

    for artist in artists:
        if keyword and not matches_keyword(
            artist,
            keyword,
            search_mode,
        ):
            continue

        if rating_value > 0 and not matches_rating_filter(
            artist,
            rating_value,
            rating_filter_mode,
        ):
            continue

        if favorite_only and not bool(artist.get("is_favorite", 0)):
            continue

        if update_required_only and artist.get("update_status") != "need_update":
            continue

        if unknown_only and artist.get("update_status") != "unknown":
            continue

        if unrated_only and int(artist.get("rating", 0) or 0) != 0:
            continue

        filtered.append(artist)

    return filtered


def matches_keyword(
    artist: dict,
    keyword: str,
    search_mode: str = "all",
) -> bool:
    targets = get_search_targets(artist, search_mode)

    return any(keyword in target for target in targets)


def get_search_targets(
    artist: dict,
    search_mode: str,
) -> list[str]:
    artist_name = str(artist.get("artist_name", "")).lower()
    pixiv_id = str(artist.get("pixiv_id", "")).lower()
    tags = get_artist_tag_search_text(artist)

    if search_mode == "artist_name":
        return [artist_name]

    if search_mode == "pixiv_id":
        return [pixiv_id]

    if search_mode == "tags":
        return [tags]

    return [
        artist_name,
        pixiv_id,
        tags,
    ]


def get_artist_tag_search_text(artist: dict) -> str:
    tags = parse_artist_tags(artist.get("artist_tags", ""))
    names = []

    for tag in tags:
        original = str(tag.get("original", "") or "").strip()
        translated = str(tag.get("translated", "") or "").strip()

        if original:
            names.append(original)

        if translated:
            names.append(translated)

    return " ".join(names).lower()


def matches_rating_filter(
    artist: dict,
    rating_value: int,
    rating_filter_mode: str,
) -> bool:
    rating = int(artist.get("rating", 0) or 0)

    if rating_filter_mode == "exact":
        return rating == rating_value

    return rating >= rating_value


def sort_artists(
    artists: list[dict],
    sort_rules: list[tuple[str, bool]],
) -> list[dict]:
    sorted_artists = artists

    for sort_field, sort_reverse in reversed(sort_rules):
        sorted_artists = sort_artists_by_field(
            sorted_artists,
            sort_field,
            sort_reverse,
        )

    return sorted_artists


def sort_artists_by_field(
    artists: list[dict],
    sort_field: str,
    sort_reverse: bool,
) -> list[dict]:
    if sort_field is None:
        return artists

    if sort_field == "artist_name":
        return sorted(
            artists,
            key=lambda artist: str(
                artist.get("artist_name", "")
            ).lower(),
            reverse=sort_reverse,
        )

    if sort_field == "pixiv_id":
        return sorted(
            artists,
            key=lambda artist: parse_int(
                artist.get("pixiv_id", 0)
            ),
            reverse=sort_reverse,
        )

    if sort_field == "folder_artwork_count":
        return sorted(
            artists,
            key=lambda artist: int(
                artist.get("folder_artwork_count", 0) or 0
            ),
            reverse=sort_reverse,
        )

    if sort_field == "missing_artwork_count":
        return sorted(
            artists,
            key=get_missing_artwork_count,
            reverse=sort_reverse,
        )

    if sort_field == "folder_file_count":
        return sorted(
            artists,
            key=lambda artist: int(
                artist.get("folder_file_count", 0) or 0
            ),
            reverse=sort_reverse,
        )

    if sort_field == "folder_size_bytes":
        return sorted(
            artists,
            key=lambda artist: int(
                artist.get("folder_size_bytes", 0) or 0
            ),
            reverse=sort_reverse,
        )

    if sort_field == "rating":
        return sorted(
            artists,
            key=lambda artist: int(
                artist.get("rating", 0) or 0
            ),
            reverse=sort_reverse,
        )

    if sort_field == "last_viewed_at":
        return sorted(
            artists,
            key=lambda artist: parse_datetime(
                artist.get("last_viewed_at")
            ),
            reverse=sort_reverse,
        )

    if sort_field == "updated_at":
        return sorted(
            artists,
            key=lambda artist: parse_datetime(
                artist.get("updated_at")
            ),
            reverse=sort_reverse,
        )

    return artists


def get_missing_artwork_count(artist: dict) -> int:
    local_ids = parse_artwork_ids(
        artist.get("local_latest_artwork_ids", "")
    )
    pixiv_ids = parse_artwork_ids(
        artist.get("pixiv_latest_artwork_ids", "")
    )

    if not pixiv_ids:
        return 0

    return len(pixiv_ids - local_ids)


def parse_artwork_ids(value) -> set[str]:
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


def parse_int(value) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def parse_datetime(value) -> datetime:
    if not value:
        return datetime.min

    if isinstance(value, datetime):
        return value

    try:
        return datetime.fromisoformat(str(value))
    except ValueError:
        return datetime.min
