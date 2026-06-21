def to_int(value) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def to_float(value) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def format_count(value) -> str:
    return f"{to_int(value):,}"


def format_number(value) -> str:
    number = to_float(value)

    if number.is_integer():
        return f"{int(number):,}"

    return f"{number:,.1f}"


def format_rating(value) -> str:
    number = to_float(value)

    if number <= 0:
        return "-"

    return f"{number:.1f}"


def format_bytes(value) -> str:
    size = to_float(value)

    if size <= 0:
        return "0 B"

    units = ["B", "KB", "MB", "GB", "TB"]
    unit_index = 0

    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1

    if unit_index == 0:
        return f"{int(size)} {units[unit_index]}"

    return f"{size:.1f} {units[unit_index]}"
