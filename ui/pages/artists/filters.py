from datetime import datetime


DEFAULT_SORT_REVERSE = {
    "artist_name": False,
    "pixiv_id": False,
    "folder_artwork_count": True,
    "folder_file_count": True,
    "rating": True,
    "last_viewed_at": True,
    "created_at": True,
}


def filter_artists(
    artists: list[dict],
    keyword: str,
    rating_value: int = 0,
    rating_filter_mode: str = "min",
    favorite_only: bool = False,
    update_required_only: bool = False,
    unknown_only: bool = False,
    unrated_only: bool = False,
    exclude_hidden: bool = False,
) -> list[dict]:
    keyword = keyword.strip().lower()

    filtered = []

    for artist in artists:
        if exclude_hidden and bool(artist.get("is_hidden", 0)):
            continue

        if keyword and not matches_keyword(artist, keyword):
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


def matches_keyword(artist: dict, keyword: str) -> bool:
    artist_name = str(artist.get("artist_name", "")).lower()
    pixiv_id = str(artist.get("pixiv_id", "")).lower()

    return keyword in artist_name or keyword in pixiv_id


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

    if sort_field == "folder_file_count":
        return sorted(
            artists,
            key=lambda artist: int(
                artist.get("folder_file_count", 0) or 0
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

    if sort_field == "created_at":
        return sorted(
            artists,
            key=lambda artist: parse_datetime(
                artist.get("created_at")
            ),
            reverse=sort_reverse,
        )

    return artists


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
