def parse_ids(value) -> list[str]:
    if not value:
        return []

    if isinstance(value, list):
        values = value
    else:
        values = str(value).split(",")

    return [
        str(item).strip()
        for item in values
        if str(item).strip()
    ]


def build_update_history_comparison(
    current_history: dict,
    previous_history: dict | None,
) -> dict:
    if previous_history is None:
        return {
            "has_previous": False,
            "previous_missing_count": None,
            "missing_delta": 0,
            "new_missing_ids": "",
            "resolved_missing_ids": "",
            "new_missing_count": 0,
            "resolved_missing_count": 0,
        }

    current_missing_count = int(
        current_history.get("missing_count", 0) or 0
    )
    previous_missing_count = int(
        previous_history.get("missing_count", 0) or 0
    )

    current_missing_ids = parse_ids(
        current_history.get("missing_ids", "")
    )
    previous_missing_ids = parse_ids(
        previous_history.get("missing_ids", "")
    )

    new_missing_ids = [
        artwork_id
        for artwork_id in current_missing_ids
        if artwork_id not in previous_missing_ids
    ]
    resolved_missing_ids = [
        artwork_id
        for artwork_id in previous_missing_ids
        if artwork_id not in current_missing_ids
    ]

    return {
        "has_previous": True,
        "previous_missing_count": previous_missing_count,
        "missing_delta": current_missing_count - previous_missing_count,
        "new_missing_ids": ",".join(new_missing_ids),
        "resolved_missing_ids": ",".join(resolved_missing_ids),
        "new_missing_count": len(new_missing_ids),
        "resolved_missing_count": len(resolved_missing_ids),
    }
