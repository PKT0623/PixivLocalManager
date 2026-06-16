def get_active_preview_result_filters(
    show_created_only: bool,
    show_updated_only: bool,
    show_error_only: bool,
) -> set[str]:
    result_filters = set()

    if show_created_only:
        result_filters.add("신규 등록 예정")

    if show_updated_only:
        result_filters.add("업데이트 예정")

    if show_error_only:
        result_filters.add("오류 예상")

    return result_filters


def matches_preview_filters(
    row_data: dict,
    show_created_only: bool,
    show_updated_only: bool,
    show_error_only: bool,
    hide_unchanged: bool,
) -> bool:
    if row_data.get("is_excluded"):
        return False

    result = str(row_data.get("preview_result", "") or "")
    active_result_filters = get_active_preview_result_filters(
        show_created_only=show_created_only,
        show_updated_only=show_updated_only,
        show_error_only=show_error_only,
    )

    if active_result_filters and result not in active_result_filters:
        return False

    if hide_unchanged and result == "변경 없음 예정":
        return False

    return True
