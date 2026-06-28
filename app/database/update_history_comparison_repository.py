from app.database.update_history_utils import build_update_history_comparison


def build_update_history_comparison_data(
    current_history: dict,
    previous_history: dict | None,
) -> dict:
    return build_update_history_comparison(
        current_history=current_history,
        previous_history=previous_history,
    )


def build_compared_update_histories(
    histories: list[dict],
) -> list[dict]:
    compared_histories = []

    for index, history in enumerate(histories):
        previous_history = None

        if index + 1 < len(histories):
            previous_history = histories[index + 1]

        compared_history = dict(history)
        compared_history.update(
            build_update_history_comparison_data(
                current_history=history,
                previous_history=previous_history,
            )
        )

        compared_histories.append(compared_history)

    return compared_histories


def build_recent_missing_increased_histories(
    recent_histories: list[dict],
    histories_by_artist_id: dict[int, list[dict]],
    limit: int = 20,
) -> list[dict]:
    artist_ids = []

    for history in recent_histories:
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

    increased_histories = []

    for artist_id in artist_ids:
        histories = histories_by_artist_id.get(artist_id, [])

        if not histories:
            continue

        latest_history = dict(histories[0])
        previous_history = histories[1] if len(histories) > 1 else None

        latest_history.update(
            build_update_history_comparison_data(
                current_history=latest_history,
                previous_history=previous_history,
            )
        )

        missing_delta = int(latest_history.get("missing_delta", 0) or 0)

        if missing_delta <= 0:
            continue

        increased_histories.append(latest_history)

        if len(increased_histories) >= limit:
            break

    return increased_histories


def collect_artist_ids_from_histories(
    histories: list[dict],
) -> list[int]:
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
