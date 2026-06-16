def build_preview_summary(
    preview_rows: list[dict],
) -> dict:
    summary = {
        "created": 0,
        "updated": 0,
        "unchanged": 0,
        "failed": 0,
        "selected": 0,
    }

    for row_data in preview_rows:
        if row_data.get("is_excluded"):
            continue

        result = str(row_data.get("preview_result", "") or "")

        if result == "신규 등록 예정":
            summary["created"] += 1
        elif result == "업데이트 예정":
            summary["updated"] += 1
        elif result == "변경 없음 예정":
            summary["unchanged"] += 1
        elif result == "오류 예상":
            summary["failed"] += 1

        if row_data.get("selected") is True:
            summary["selected"] += 1

    return summary
