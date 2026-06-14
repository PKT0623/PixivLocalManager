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
    from .columns import COLUMN_RATING, COLUMN_STATUS

    if column == COLUMN_STATUS:
        return format_status(value)

    if column == COLUMN_RATING:
        return format_rating(value, rating_display_mode)

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
