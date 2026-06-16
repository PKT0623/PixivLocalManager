from .statistics_formatter import format_diff


def format_recent_scan_history(
    history: list[dict],
) -> str:
    if not history:
        return "최근 스캔 기록이 없습니다."

    lines = []

    for index, item in enumerate(history[:10], start=1):
        finished_at = str(item.get("finished_at_text", "-") or "-")
        total = int(item.get("total", 0) or 0)
        created = int(item.get("created", 0) or 0)
        updated = int(item.get("updated", 0) or 0)
        failed = int(item.get("failed", 0) or 0)

        lines.append(
            f"{index}. {finished_at} / 대상 {total}개 / "
            f"등록 {created}, 업데이트 {updated}, 실패 {failed}"
        )

    return "\n".join(lines)


def format_scan_compare_info(
    compare_result: dict | None,
) -> str:
    if not compare_result:
        return "비교할 이전 스캔 기록이 없습니다."

    items = compare_result.get("items", [])

    if not items:
        return "비교할 이전 스캔 기록이 없습니다."

    parts = []

    for item in items:
        label = str(item.get("label", "-") or "-")
        diff = int(item.get("diff", 0) or 0)
        parts.append(
            f"{label} {format_diff(diff)}"
        )

    latest_finished_at = str(
        compare_result.get("latest_finished_at", "-") or "-"
    )
    previous_finished_at = str(
        compare_result.get("previous_finished_at", "-") or "-"
    )

    return (
        f"{previous_finished_at} → {latest_finished_at}\n"
        + " / ".join(parts)
    )
