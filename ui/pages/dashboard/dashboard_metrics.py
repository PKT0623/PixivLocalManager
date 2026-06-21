from .utils import (
    count_status,
    format_bytes,
    format_datetime_short,
    is_today,
    to_int,
)


def calculate_dashboard_summary(
    artists: list[dict],
    update_status_summary: dict,
    follow_user_count: int = 0,
    bookmark_artwork_count: int = 0,
) -> dict:
    total_artists = len(artists)
    total_artworks = calculate_total_artworks(artists)
    total_files = calculate_total_files(artists)
    total_folder_size = calculate_total_folder_size(artists)

    return {
        "total_artists": total_artists,
        "favorite_artists": calculate_favorite_artists(artists),
        "follow_users": follow_user_count,
        "bookmark_artworks": bookmark_artwork_count,
        "need_update_count": count_status(artists, {"need_update"}),
        "error_count": count_status(artists, {"error"}),
        "recent_scan": calculate_recent_scan_time(artists),
        "total_artworks": total_artworks,
        "total_files": total_files,
        "total_folder_size": format_bytes(total_folder_size),
        "update_status_summary": update_status_summary,
    }


def calculate_update_status_summary(
    artists: list[dict],
    today_histories: list[dict],
    latest_histories: list[dict],
    history_repo,
) -> dict:
    today_checked_histories = [
        history
        for history in today_histories
        if history.get("action") != "skipped_recent"
    ]

    today_comparison = calculate_today_comparison(
        today_histories=today_checked_histories,
        history_repo=history_repo,
    )

    return {
        "total_missing_count": calculate_total_missing_count(
            latest_histories
        ),
        "today_update_count": len(today_checked_histories),
        "today_new_missing_count": today_comparison["new_missing_count"],
        "today_resolved_missing_count": (
            today_comparison["resolved_missing_count"]
        ),
        "latest_count": count_status(artists, {"latest", "up_to_date"}),
        "need_update_count": count_status(artists, {"need_update"}),
        "unknown_count": count_status(artists, {"unknown"}),
        "error_count": count_status(artists, {"error"}),
    }


def calculate_today_comparison(
    today_histories: list[dict],
    history_repo,
) -> dict:
    new_missing_count = 0
    resolved_missing_count = 0

    for history in today_histories:
        if not is_today(history.get("checked_at")):
            continue

        artist_id = history.get("artist_id")

        if artist_id is None:
            continue

        histories = history_repo.get_by_artist_id(
            artist_id=int(artist_id),
            limit=20,
        )
        previous_history = find_previous_history(
            histories=histories,
            current_history=history,
        )

        comparison = history_repo.build_comparison(
            current_history=history,
            previous_history=previous_history,
        )

        new_missing_count += int(
            comparison.get("new_missing_count", 0) or 0
        )
        resolved_missing_count += int(
            comparison.get("resolved_missing_count", 0) or 0
        )

    return {
        "new_missing_count": new_missing_count,
        "resolved_missing_count": resolved_missing_count,
    }


def find_previous_history(
    histories: list[dict],
    current_history: dict,
):
    current_id = current_history.get("id")
    current_checked_at = str(current_history.get("checked_at", "") or "")

    for history in histories:
        if current_id is not None and history.get("id") == current_id:
            continue

        history_checked_at = str(history.get("checked_at", "") or "")

        if history_checked_at > current_checked_at:
            continue

        return history

    return None


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
    recent_histories: list[dict],
    limit: int = 10,
) -> dict:
    valid_histories = [
        history
        for history in recent_histories
        if history.get("action") != "skipped_recent"
    ]

    return {
        "recent_scan_results": valid_histories[:limit],
    }


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


def calculate_total_missing_count(latest_histories: list[dict]) -> int:
    return sum(
        to_int(history.get("missing_count", 0))
        for history in latest_histories
        if history.get("action") != "skipped_recent"
    )


def calculate_recent_scan_time(artists: list[dict]) -> str:
    scan_times = [
        str(artist.get("last_checked_at", "") or "")
        for artist in artists
        if artist.get("last_checked_at")
    ]

    if not scan_times:
        return "-"

    return format_datetime_short(max(scan_times))
