from datetime import datetime, timedelta


def format_datetime(value) -> str:
    if value is None or value == "":
        return "-"

    try:
        dt = datetime.fromisoformat(str(value))
        return dt.strftime("%Y-%m-%d %H:%M")
    except ValueError:
        return str(value)


def was_recently_checked(
    artist: dict,
    hours: int = 6,
) -> bool:
    last_checked_at = artist.get("last_checked_at")

    if not last_checked_at:
        return False

    try:
        checked_at = datetime.fromisoformat(last_checked_at)
    except ValueError:
        return False

    return datetime.now() - checked_at < timedelta(hours=hours)


def exclude_recently_checked(
    artists: list[dict],
    artist_ids: list[int],
    hours: int = 6,
) -> list[int]:
    artist_map = {
        int(artist["id"]): artist
        for artist in artists
        if artist.get("id") is not None
    }

    result = []

    for artist_id in artist_ids:
        artist = artist_map.get(artist_id)

        if artist is None:
            continue

        if was_recently_checked(
            artist,
            hours=hours,
        ):
            continue

        result.append(artist_id)

    return result
