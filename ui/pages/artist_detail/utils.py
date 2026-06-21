from datetime import datetime
from pathlib import Path
import re


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


IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".webp",
    ".bmp",
}

ARTWORK_ID_PATTERN = re.compile(r"(\d{5,})")
PAGE_INDEX_PATTERN = re.compile(r"_p(\d+)")


def display_value(value) -> str:
    if value is None or value == "":
        return "-"

    return str(value)


def status_label(value) -> str:
    if value is None or value == "":
        return "-"

    return STATUS_LABELS.get(str(value), str(value))


def format_datetime(value) -> str:
    if value is None or value == "":
        return "-"

    text = str(value)

    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return text

    return parsed.strftime("%Y-%m-%d %H:%M")


def format_timestamp(value: float) -> str:
    try:
        parsed = datetime.fromtimestamp(value)
    except (OSError, OverflowError, ValueError):
        return "-"

    return parsed.strftime("%Y-%m-%d %H:%M")


def format_file_size(size_bytes) -> str:
    try:
        size = float(size_bytes or 0)
    except (TypeError, ValueError):
        size = 0

    if size <= 0:
        return "0 B"

    units = ["B", "KB", "MB", "GB", "TB"]

    for unit in units:
        if size < 1024 or unit == units[-1]:
            if unit == "B":
                return f"{int(size)} {unit}"

            return f"{size:.1f} {unit}"

        size /= 1024

    return "0 B"


def folder_status_label(folder_path: str) -> str:
    folder_path = str(folder_path or "").strip()

    if not folder_path or folder_path == "-":
        return "경로 비어있음"

    path = Path(folder_path)

    if not path.exists():
        return "폴더 없음"

    if not path.is_dir():
        return "폴더 경로 아님"

    return "정상"


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


def parse_id_text(value) -> list[str]:
    if not value:
        return []

    ids = []

    for item in str(value).split(","):
        artwork_id = item.strip()

        if artwork_id:
            ids.append(artwork_id)

    return ids


def calculate_missing_artwork_ids(
    local_ids: list[str],
    pixiv_ids: list[str],
) -> list[str]:
    local_id_set = set(local_ids)
    pixiv_id_set = set(pixiv_ids)

    missing_ids = pixiv_id_set - local_id_set

    return sorted(
        missing_ids,
        key=sort_artwork_id,
        reverse=True,
    )


def find_recent_local_artworks(
    folder_path: str,
    limit: int = 10,
) -> list[dict]:
    folder_path = str(folder_path or "").strip()

    if not folder_path or folder_path == "-":
        return []

    root_path = Path(folder_path)

    if not root_path.exists() or not root_path.is_dir():
        return []

    artwork_map = {}

    for file_path in root_path.rglob("*"):
        if not file_path.is_file():
            continue

        if file_path.suffix.lower() not in IMAGE_EXTENSIONS:
            continue

        artwork_id = extract_artwork_id(file_path.stem)

        if not artwork_id:
            continue

        page_index = extract_page_index(file_path.stem)
        modified_at = file_path.stat().st_mtime

        current_item = artwork_map.get(artwork_id)

        if current_item is None:
            artwork_map[artwork_id] = {
                "artwork_id": artwork_id,
                "file_path": str(file_path),
                "page_index": page_index,
                "file_count": 1,
                "latest_modified_at": modified_at,
            }
            continue

        current_item["file_count"] += 1
        current_item["latest_modified_at"] = max(
            current_item["latest_modified_at"],
            modified_at,
        )

        if page_index < current_item["page_index"]:
            current_item["file_path"] = str(file_path)
            current_item["page_index"] = page_index

    artworks = list(artwork_map.values())

    artworks.sort(
        key=lambda item: sort_artwork_id(item["artwork_id"]),
        reverse=True,
    )

    return [
        {
            "artwork_id": artwork["artwork_id"],
            "file_path": artwork["file_path"],
            "file_count": artwork["file_count"],
            "latest_modified_at": format_timestamp(
                artwork["latest_modified_at"]
            ),
        }
        for artwork in artworks[:limit]
    ]


def extract_artwork_id(file_stem: str) -> str:
    match = ARTWORK_ID_PATTERN.search(file_stem)

    if match is None:
        return ""

    return match.group(1)


def extract_page_index(file_stem: str) -> int:
    match = PAGE_INDEX_PATTERN.search(file_stem)

    if match is None:
        return 999999

    try:
        return int(match.group(1))
    except ValueError:
        return 999999


def sort_artwork_id(value: str):
    try:
        return int(value)
    except ValueError:
        return value

