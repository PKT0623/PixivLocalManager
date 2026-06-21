import json
from datetime import datetime


STATUS_LABELS = {
    "normal": "일반",
    "active": "활성",
    "inactive": "비활성",
    "unknown": "업데이트 미확인",
    "latest": "최신 상태",
    "up_to_date": "최신 상태",
    "need_update": "업데이트 필요",
    "updated": "업데이트 완료",
    "error": "확인 실패",
}


def format_cell_value(
    column: int,
    value,
    rating_display_mode: str,
) -> str:
    from .columns import (
        COLUMN_FAVORITE,
        COLUMN_FOLDER_SIZE,
        COLUMN_LAST_VIEWED_AT,
        COLUMN_RATING,
        COLUMN_STATUS,
        COLUMN_TAGS,
        COLUMN_UPDATED_AT,
    )

    if column == COLUMN_STATUS:
        return format_status(value)

    if column == COLUMN_RATING:
        return format_rating(value, rating_display_mode)

    if column == COLUMN_TAGS:
        return format_artist_tags(value)

    if column == COLUMN_FOLDER_SIZE:
        return format_file_size(value)

    if column in (
        COLUMN_LAST_VIEWED_AT,
        COLUMN_UPDATED_AT,
    ):
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
        key=lambda item: (
            item.get("artwork_count", 0),
            item.get("original", ""),
        ),
        reverse=True,
    )

    display_names = []

    for tag in tags:
        translated = str(tag.get("translated", "") or "").strip()
        original = str(tag.get("original", "") or "").strip()

        if translated:
            display_names.append(translated)
        elif original:
            display_names.append(original)

    if not display_names:
        return "-"

    return ", ".join(display_names)


def parse_artist_tags(value) -> list[dict]:
    if not value:
        return []

    if isinstance(value, list):
        return [
            normalize_tag_dict(tag)
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

        result.append(
            normalize_tag_dict(item)
        )

    return result


def normalize_tag_dict(item: dict) -> dict:
    return {
        "original": str(
            item.get("original")
            or item.get("name")
            or item.get("tag")
            or ""
        ).strip(),
        "translated": str(
            item.get("translated")
            or item.get("translated_name")
            or item.get("tag_translation")
            or ""
        ).strip(),
        "artwork_count": to_non_negative_int(
            item.get("artwork_count")
            or item.get("count")
            or item.get("cnt")
            or 0
        ),
    }


def parse_legacy_tags(value: str) -> list[dict]:
    result = []

    for tag_name in value.replace("\n", ",").split(","):
        tag_name = tag_name.strip()

        if not tag_name:
            continue

        result.append(
            {
                "original": tag_name,
                "translated": "",
                "artwork_count": 0,
            }
        )

    return result


def to_non_negative_int(value) -> int:
    try:
        return max(0, int(value))
    except (TypeError, ValueError):
        return 0


def format_file_size(value) -> str:
    try:
        size = int(value or 0)
    except (TypeError, ValueError):
        size = 0

    if size <= 0:
        return "-"

    units = ["B", "KB", "MB", "GB", "TB"]
    unit_index = 0
    display_size = float(size)

    while display_size >= 1024 and unit_index < len(units) - 1:
        display_size /= 1024
        unit_index += 1

    if unit_index == 0:
        return f"{int(display_size)} {units[unit_index]}"

    return f"{display_size:.1f} {units[unit_index]}"


def format_datetime(value) -> str:
    if not value:
        return "-"

    text = str(value)

    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return text

    return parsed.strftime("%Y-%m-%d %H:%M")
