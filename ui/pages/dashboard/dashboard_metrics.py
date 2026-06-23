from .utils import (
    count_status,
    format_bytes,
    format_datetime_short,
    is_today,
    to_int,
)


UPDATE_STATUS_LABELS = {
    "latest": "최신",
    "up_to_date": "최신",
    "need_update": "업데이트 필요",
    "unknown": "미확인",
    "error": "오류",
}


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
    current_state_comparison = calculate_current_state_comparison(
        artists=artists,
        latest_histories=latest_histories,
    )

    return {
        "total_missing_count": calculate_total_missing_count_from_artists(
            artists
        ),
        "today_update_count": len(today_checked_histories),
        "today_new_missing_count": (
            today_comparison["new_missing_count"]
            + current_state_comparison["new_missing_count"]
        ),
        "today_resolved_missing_count": (
            today_comparison["resolved_missing_count"]
            + current_state_comparison["resolved_missing_count"]
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
    histories_by_artist_id = history_repo.get_by_artist_ids(
        artist_ids=get_history_artist_ids(today_histories),
        limit_per_artist=20,
    )

    for history in today_histories:
        if not is_today(history.get("checked_at")):
            continue

        artist_id = history.get("artist_id")

        if artist_id is None:
            continue

        try:
            normalized_artist_id = int(artist_id)
        except (TypeError, ValueError):
            continue

        histories = histories_by_artist_id.get(normalized_artist_id, [])
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


def calculate_current_state_comparison(
    artists: list[dict],
    latest_histories: list[dict],
) -> dict:
    artists_by_id = build_artist_map(artists)
    latest_histories_by_artist_id = build_latest_history_map(
        latest_histories
    )
    new_missing_count = 0
    resolved_missing_count = 0

    for artist_id, artist in artists_by_id.items():
        latest_history = latest_histories_by_artist_id.get(artist_id)

        if latest_history is None:
            continue

        if latest_history.get("action") == "skipped_recent":
            continue

        current_missing_ids = calculate_missing_artwork_ids(artist)
        latest_missing_ids = set(
            parse_artwork_ids(latest_history.get("missing_ids", ""))
        )

        new_missing_count += len(current_missing_ids - latest_missing_ids)
        resolved_missing_count += len(
            latest_missing_ids - current_missing_ids
        )

    return {
        "new_missing_count": new_missing_count,
        "resolved_missing_count": resolved_missing_count,
    }


def build_artist_map(
    artists: list[dict],
) -> dict[int, dict]:
    artists_by_id = {}

    for artist in artists:
        artist_id = artist.get("id")

        if artist_id is None:
            continue

        try:
            normalized_artist_id = int(artist_id)
        except (TypeError, ValueError):
            continue

        artists_by_id[normalized_artist_id] = artist

    return artists_by_id


def build_latest_history_map(
    latest_histories: list[dict],
) -> dict[int, dict]:
    latest_histories_by_artist_id = {}

    for history in latest_histories:
        artist_id = history.get("artist_id")

        if artist_id is None:
            continue

        try:
            normalized_artist_id = int(artist_id)
        except (TypeError, ValueError):
            continue

        current_history = latest_histories_by_artist_id.get(
            normalized_artist_id
        )

        if current_history is None:
            latest_histories_by_artist_id[normalized_artist_id] = history
            continue

        if is_newer_history(history, current_history):
            latest_histories_by_artist_id[normalized_artist_id] = history

    return latest_histories_by_artist_id


def is_newer_history(
    history: dict,
    target_history: dict,
) -> bool:
    history_checked_at = str(history.get("checked_at", "") or "")
    target_checked_at = str(target_history.get("checked_at", "") or "")

    if history_checked_at != target_checked_at:
        return history_checked_at > target_checked_at

    return to_int(history.get("id", 0)) > to_int(target_history.get("id", 0))


def get_history_artist_ids(histories: list[dict]) -> list[int]:
    artist_ids = []

    for history in histories:
        artist_id = history.get("artist_id")

        if artist_id is None:
            continue

        try:
            normalized_artist_id = int(artist_id)
        except (TypeError, ValueError):
            continue

        if normalized_artist_id in artist_ids:
            continue

        artist_ids.append(normalized_artist_id)

    return artist_ids


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
