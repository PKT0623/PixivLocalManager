import json
from datetime import datetime


SYNC_STATUS_LABELS = {
    "pending": "대기",
    "synced": "완료",
    "failed": "실패",
    "skipped": "스킵",
}


def format_tags(
    value,
    prefer_translated: bool = False,
) -> str:
    text = str(value or "").strip()

    if not text:
        return "-"

    try:
        tags = json.loads(text)
    except json.JSONDecodeError:
        return text

    if not isinstance(tags, list):
        return text

    names = []

    for tag in tags:
        if not isinstance(tag, dict):
            continue

        original = str(tag.get("original", "") or "").strip()
        translated = str(tag.get("translated", "") or "").strip()

        if prefer_translated and translated:
            names.append(translated)
        elif original:
            names.append(original)
        elif translated:
            names.append(translated)

    if not names:
        return "-"

    return ", ".join(names)


def format_sync_status(
    item: dict,
) -> str:
    status = str(item.get("sync_status", "") or "pending")
    label = SYNC_STATUS_LABELS.get(status, status)

    retry_count = int(item.get("sync_retry_count", 0) or 0)

    if status == "failed" and retry_count > 0:
        return f"{label}({retry_count})"

    return label


def format_datetime(
    value,
) -> str:
    text = str(value or "").strip()

    if not text:
        return "-"

    return text.replace("T", " ")[:16]


def format_local_match(
    item: dict,
) -> str:
    if item.get("is_local_artist"):
        return "등록"

    return "미등록"


def empty_to_dash(
    value,
) -> str:
    text = str(value or "").strip()

    if not text:
        return "-"

    return text


def to_int(
    value,
) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return -1


def to_datetime(
    value,
) -> datetime:
    text = str(value or "").strip()

    if not text:
        return datetime.min

    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return datetime.min
