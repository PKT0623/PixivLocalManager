import re
from datetime import datetime
from pathlib import Path


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


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
