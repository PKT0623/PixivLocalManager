STATUS_SORT_ORDERS = [
    ["unknown", "up_to_date", "latest", "need_update", "updated", "error"],
    ["up_to_date", "latest", "need_update", "updated", "unknown", "error"],
    ["need_update", "updated", "unknown", "up_to_date", "latest", "error"],
]

DEFAULT_SORT_REVERSE = {
    "artist_name": False,
    "folder_artwork_count": True,
    "rating": True,
}


def filter_artists(artists: list[dict], keyword: str) -> list[dict]:
    keyword = keyword.strip().lower()

    if not keyword:
        return list(artists)

    filtered = []

    for artist in artists:
        artist_name = str(artist.get("artist_name", "")).lower()
        pixiv_id = str(artist.get("pixiv_id", "")).lower()

        if keyword in artist_name or keyword in pixiv_id:
            filtered.append(artist)

    return filtered


def sort_artists(
    artists: list[dict],
    sort_field: str,
    sort_reverse: bool,
    status_sort_index: int,
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

    if sort_field == "folder_artwork_count":
        return sorted(
            artists,
            key=lambda artist: int(
                artist.get("folder_artwork_count", 0) or 0
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

    if sort_field == "update_status":
        return sort_by_status(
            artists,
            status_sort_index,
        )

    return artists


def sort_by_status(
    artists: list[dict],
    status_sort_index: int,
) -> list[dict]:
    status_order = STATUS_SORT_ORDERS[status_sort_index]

    status_rank = {
        status: index
        for index, status in enumerate(status_order)
    }

    return sorted(
        artists,
        key=lambda artist: status_rank.get(
            str(artist.get("update_status", "")),
            len(status_rank),
        ),
    )
