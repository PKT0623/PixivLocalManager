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


def display_value(value) -> str:
    if value is None or value == "":
        return "-"

    return str(value)


def status_label(value) -> str:
    if value is None or value == "":
        return "-"

    return STATUS_LABELS.get(str(value), str(value))


def to_int(value, minimum: int = 0, maximum: int = 999999) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError):
        number = minimum

    return max(minimum, min(maximum, number))


def parse_non_negative_int(value: str, field_label: str) -> int:
    value = value.strip()

    if not value:
        raise ValueError(f"{field_label}는 비워둘 수 없습니다.")

    try:
        number = int(value)
    except ValueError as error:
        raise ValueError(f"{field_label}는 0 이상의 정수여야 합니다.") from error

    if number < 0:
        raise ValueError(f"{field_label}는 0 이상의 정수여야 합니다.")

    return number


def parse_rating(value: str) -> int:
    rating = parse_non_negative_int(value, "평점")

    if rating > 10:
        raise ValueError("평점은 0부터 10까지의 정수여야 합니다.")

    return rating
