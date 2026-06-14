import json
from datetime import datetime


STATUS_LABELS = {
    "active": "활성",
    "inactive": "비활성",
    "unknown": "미확인",
    "latest": "최신",
    "up_to_date": "최신",
    "need_update": "업데이트 필요",
    "updated": "업데이트 완료",
    "error": "오류",
}


def format_cell_value(
    column: int,
    value,
    rating_display_mode: str,
) -> str:
    from .columns import (
        COLUMN_FAVORITE,
        COLUMN_LAST_VIEWED_AT,
        COLUMN_RATING,
        COLUMN_STATUS,
        COLUMN_TAGS,
    )

    if column == COLUMN_STATUS:
        return format_status(value)

    if column == COLUMN_RATING:
        return format_rating(value, rating_display_mode)

    if column == COLUMN_TAGS:
        return format_artist_tags(value)

    if column == COLUMN_LAST_VIEWED_AT:
        return format_datetime(value)

    if column == COLUMN_FAVORITE:
        return "★" if bool(value) else "☆"

    if value is None or value == "":
        return "-"

    return str(value)


def format_status(value) -> str:
    if value is None or value == "":
        return "-"

    return STATUS_LABELS.get(str(value), str(value))


def format_rating(value, rating_display_mode: str) -> str:
    try:
        rating = int(value)
    except (TypeError, ValueError):
        rating = 0

    rating = max(0, min(10, rating))

    if rating_display_mode == "number":
        return f"{rating}/10"

    return rating_to_stars(rating)


def rating_to_stars(rating: int) -> str:
    if rating <= 0:
        return "-"

    full_stars = rating // 2
    has_half_score = rating % 2 == 1

    stars = "★" * full_stars

    if has_half_score:
        stars += "☆"

    return stars


def format_artist_tags(value) -> str:
    tags = parse_artist_tags(value)

    if not tags:
        return "-"

    tags.sort(
        key=lambda item: item.get("artwork_count", 0),
        reverse=True,
    )

    display_names = []

    for tag in tags[:3]:
        translated_name = str(tag.get("translated_name", "")).strip()
        original_name = str(tag.get("name", "")).strip()

        if translated_name:
            display_names.append(translated_name)
        elif original_name:
            display_names.append(original_name)

    if not display_names:
        return "-"

    return ", ".join(display_names)


def parse_artist_tags(value) -> list[dict]:
    if not value:
        return []

    if isinstance(value, list):
        return [
            tag
            for tag in value
            if isinstance(tag, dict)
        ]

    try:
        parsed = json.loads(str(value))
    except json.JSONDecodeError:
        return parse_legacy_tags(str(value))

    if not isinstance(parsed, list):
        return []

    result = []

    for item in parsed:
        if not isinstance(item, dict):
            continue

        try:
            artwork_count = int(item.get("artwork_count", 0) or 0)
        except (TypeError, ValueError):
            artwork_count = 0

        result.append(
            {
                "name": str(item.get("name", "")).strip(),
                "translated_name": str(
                    item.get("translated_name", "")
                ).strip(),
                "artwork_count": max(0, artwork_count),
            }
        )

    return result


def parse_legacy_tags(value: str) -> list[dict]:
    result = []

    for tag_name in value.split(","):
        tag_name = tag_name.strip()

        if not tag_name:
            continue

        result.append(
            {
                "name": tag_name,
                "translated_name": "",
                "artwork_count": 0,
            }
        )

    return result


def format_datetime(value) -> str:
    if not value:
        return "-"

    text = str(value)

    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return text

    return parsed.strftime("%Y-%m-%d %H:%M")
