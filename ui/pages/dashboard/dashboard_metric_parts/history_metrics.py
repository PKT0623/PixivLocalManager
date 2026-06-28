from ..utils import count_status, is_today, to_int
from .artwork_metrics import (
    calculate_missing_artwork_ids,
    calculate_total_missing_count_from_artists,
    parse_artwork_ids,
)


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
