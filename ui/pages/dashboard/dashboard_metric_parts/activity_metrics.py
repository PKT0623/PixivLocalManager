from ..utils import to_int
from .artwork_metrics import calculate_missing_artwork_ids
from .constants import UPDATE_STATUS_LABELS
from .history_metrics import build_latest_history_map


def build_recent_activity_data(
    artists: list[dict],
    recent_histories: list[dict],
    recent_error_histories: list[dict],
    missing_increased_histories: list[dict],
    limit: int = 50,
) -> dict:
    return {
        "recent_viewed_artists": get_recent_artists_by_field(
            artists,
            "last_viewed_at",
            limit=limit,
        ),
        "recent_registered_artists": get_recent_artists_by_field(
            artists,
            "created_at",
            limit=limit,
        ),
        "recent_checked_artists": get_recent_artists_by_field(
            artists,
            "last_checked_at",
            limit=limit,
        ),
        "recent_update_histories": recent_histories[:limit],
        "recent_error_histories": recent_error_histories[:limit],
        "missing_increased_histories": missing_increased_histories[:limit],
    }


def build_scan_statistics_data(
    artists: list[dict],
    latest_histories: list[dict],
    limit: int = 50,
) -> dict:
    latest_histories_by_artist_id = build_latest_history_map(
        latest_histories
    )
    rows = []

    for artist in artists:
        artist_id = artist.get("id")

        if artist_id is None:
            continue

        try:
            normalized_artist_id = int(artist_id)
        except (TypeError, ValueError):
            continue

        latest_history = latest_histories_by_artist_id.get(
            normalized_artist_id,
            {},
        )
        checked_at = (
            artist.get("last_checked_at")
            or latest_history.get("checked_at")
            or ""
        )

        if not checked_at:
            continue

        rows.append(
            {
                "artist_name": artist.get("artist_name", ""),
                "result_label": status_to_label(
                    artist.get("update_status")
                ),
                "missing_count": len(calculate_missing_artwork_ids(artist)),
                "checked_at": checked_at,
            }
        )

    return {
        "recent_scan_results": sorted(
            rows,
            key=lambda row: str(row.get("checked_at", "") or ""),
            reverse=True,
        )[:limit],
    }


def status_to_label(status) -> str:
    return UPDATE_STATUS_LABELS.get(
        str(status or ""),
        "-",
    )


def build_top_ranking_data(
    artists: list[dict],
    limit: int = 50,
) -> dict:
    return {
        "artwork_top": get_top_artists_by_field(
            artists=artists,
            field_name="folder_artwork_count",
            limit=limit,
        ),
        "file_top": get_top_artists_by_field(
            artists=artists,
            field_name="folder_file_count",
            limit=limit,
        ),
        "folder_size_top": get_top_artists_by_field(
            artists=artists,
            field_name="folder_size_bytes",
            limit=limit,
            maximum=10**18,
        ),
    }


def get_top_artists_by_field(
    artists: list[dict],
    field_name: str,
    limit: int = 50,
    maximum: int = 999999,
) -> list[dict]:
    valid_artists = [
        artist
        for artist in artists
        if to_int(artist.get(field_name, 0), maximum=maximum) > 0
    ]

    return sorted(
        valid_artists,
        key=lambda artist: to_int(
            artist.get(field_name, 0),
            maximum=maximum,
        ),
        reverse=True,
    )[:limit]


def get_recent_artists_by_field(
    artists: list[dict],
    field_name: str,
    limit: int = 50,
) -> list[dict]:
    valid_artists = [
        artist
        for artist in artists
        if artist.get(field_name)
    ]

    return sorted(
        valid_artists,
        key=lambda artist: str(artist.get(field_name, "") or ""),
        reverse=True,
    )[:limit]
