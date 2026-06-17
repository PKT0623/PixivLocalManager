import re
from datetime import datetime
from pathlib import Path


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif"}


def count_status(artists: list[dict], statuses: set[str]) -> int:
    return sum(
        1
        for artist in artists
        if str(artist.get("update_status", "")) in statuses
    )


def find_latest_p0_image(folder_path):
    if not folder_path:
        return None

    folder = Path(folder_path)

    if not folder.exists() or not folder.is_dir():
        return None

    candidates = []

    for file_path in folder.iterdir():
        if not file_path.is_file():
            continue

        if file_path.suffix.lower() not in IMAGE_EXTENSIONS:
            continue

        match = re.search(r"(\d+)_p0", file_path.name)

        if match is None:
            continue

        candidates.append((int(match.group(1)), file_path))

    if not candidates:
        return None

    candidates.sort(key=lambda item: item[0], reverse=True)

    return candidates[0][1]


def format_datetime(value) -> str:
    if value is None or value == "":
        return "-"

    text = str(value)

    try:
        dt = datetime.fromisoformat(text)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        return text


def format_datetime_short(value) -> str:
    if value is None or value == "":
        return "-"

    text = str(value)

    try:
        dt = datetime.fromisoformat(text)
        return dt.strftime("%Y-%m-%d %H:%M")
    except ValueError:
        return text


def format_bytes(value) -> str:
    size = to_int(value, maximum=10**18)

    if size <= 0:
        return "0 B"

    units = ["B", "KB", "MB", "GB", "TB"]
    unit_index = 0
    display_size = float(size)

    while display_size >= 1024 and unit_index < len(units) - 1:
        display_size /= 1024
        unit_index += 1

    if unit_index == 0:
        return f"{int(display_size)} {units[unit_index]}"

    return f"{display_size:.1f} {units[unit_index]}"


def format_count(value) -> str:
    return f"{to_int(value):,}"


def format_signed_number(value) -> str:
    try:
        number = int(value)
    except (TypeError, ValueError):
        return "-"

    if number > 0:
        return f"+{number}"

    return str(number)


def format_missing_ids(values, limit: int = 3) -> str:
    ids = parse_ids(values)

    if not ids:
        return "-"

    if len(ids) <= limit:
        return ", ".join(ids)

    return f"{', '.join(ids[:limit])} 외 {len(ids) - limit}개"


def is_today(value) -> bool:
    if value is None or value == "":
        return False

    try:
        dt = datetime.fromisoformat(str(value))
    except ValueError:
        return False

    return dt.date() == datetime.now().date()


def parse_ids(values) -> list[str]:
    if not values:
        return []

    if isinstance(values, str):
        raw_values = values.split(",")
    else:
        raw_values = values

    return [
        str(value).strip()
        for value in raw_values
        if str(value).strip()
    ]


def to_int(value, minimum: int = 0, maximum: int = 999999) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError):
        number = minimum

    return max(minimum, min(maximum, number))


def clear_layout(layout):
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()

        if widget is not None:
            widget.deleteLater()
