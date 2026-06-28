from ..utils import format_bytes, format_datetime_short, to_int


def calculate_total_artworks(artists: list[dict]) -> int:
    return sum(
        to_int(artist.get("folder_artwork_count", 0))
        for artist in artists
    )


def calculate_total_files(artists: list[dict]) -> int:
    return sum(
        to_int(artist.get("folder_file_count", 0))
        for artist in artists
    )


def calculate_total_folder_size(artists: list[dict]) -> int:
    return sum(
        to_int(
            artist.get("folder_size_bytes", 0),
            maximum=10**18,
        )
        for artist in artists
    )


def calculate_favorite_artists(artists: list[dict]) -> int:
    return sum(
        1
        for artist in artists
        if bool(artist.get("is_favorite", 0))
    )


def calculate_total_missing_count_from_artists(
    artists: list[dict],
) -> int:
    return sum(
        len(calculate_missing_artwork_ids(artist))
        for artist in artists
    )


def calculate_missing_artwork_ids(
    artist: dict,
) -> set[str]:
    local_ids = set(
        parse_artwork_ids(artist.get("local_latest_artwork_ids", ""))
    )
    pixiv_ids = set(
        parse_artwork_ids(artist.get("pixiv_latest_artwork_ids", ""))
    )

    if not pixiv_ids:
        return set()

    return pixiv_ids - local_ids


def parse_artwork_ids(value) -> list[str]:
    if not value:
        return []

    if isinstance(value, (list, tuple, set)):
        values = value
    else:
        values = str(value).replace("\n", ",").split(",")

    return [
        str(item).strip()
        for item in values
        if str(item).strip()
    ]


def calculate_recent_scan_time(artists: list[dict]) -> str:
    scan_times = [
        str(artist.get("last_checked_at", "") or "")
        for artist in artists
        if artist.get("last_checked_at")
    ]

    if not scan_times:
        return "-"

    return format_datetime_short(max(scan_times))


def format_total_folder_size(artists: list[dict]) -> str:
    return format_bytes(calculate_total_folder_size(artists))
