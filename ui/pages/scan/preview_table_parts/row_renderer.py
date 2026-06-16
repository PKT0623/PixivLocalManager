from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QTableWidgetItem


PREVIEW_RESULT_COLORS = {
    "신규 등록 예정": "#198754",
    "업데이트 예정": "#0d6efd",
    "변경 없음 예정": "#6c757d",
    "오류 예상": "#dc3545",
    "제외": "#adb5bd",
}


def render_preview_rows(
    table,
    rows: list[dict],
):
    table.blockSignals(True)
    table.setRowCount(0)

    for row_data in rows:
        append_preview_row(table, row_data)

    table.blockSignals(False)


def append_preview_row(
    table,
    row_data: dict,
):
    row = table.rowCount()
    table.insertRow(row)

    can_scan = bool(row_data.get("can_scan", False))
    is_excluded = bool(row_data.get("is_excluded", False))
    is_selected = bool(row_data.get("selected", False))

    check_item = QTableWidgetItem("")
    check_item.setData(Qt.UserRole, row_data)
    check_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)

    if can_scan and not is_excluded:
        check_item.setFlags(
            Qt.ItemIsEnabled
            | Qt.ItemIsUserCheckable
            | Qt.ItemIsSelectable
        )
        check_item.setCheckState(
            Qt.Checked if is_selected else Qt.Unchecked
        )
    else:
        check_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
        check_item.setCheckState(Qt.Unchecked)

    table.setItem(row, 0, check_item)

    values = [
        get_display_preview_result(row_data),
        row_data.get("artist_name", "-"),
        row_data.get("pixiv_id", "-"),
        row_data.get("artwork_count", "-"),
        row_data.get("file_count", "-"),
        row_data.get("folder_path", "-"),
        row_data.get("message", "-"),
    ]

    for index, value in enumerate(values, start=1):
        item = QTableWidgetItem(str(value))
        item.setData(Qt.UserRole, row_data)
        apply_preview_item_alignment(item, index)
        apply_preview_item_color(item, index, values, is_excluded)
        table.setItem(row, index, item)


def get_display_preview_result(
    row_data: dict,
) -> str:
    if row_data.get("is_excluded"):
        return "제외"

    return str(row_data.get("preview_result", "") or "-")


def apply_preview_item_alignment(
    item: QTableWidgetItem,
    column: int,
):
    if column in (0, 1, 3, 4, 5):
        item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
    else:
        item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)


def apply_preview_item_color(
    item: QTableWidgetItem,
    column: int,
    values: list,
    is_excluded: bool,
):
    if is_excluded:
        item.setForeground(QColor("#666666"))
        item.setBackground(QColor("#f1f3f5"))
        return

    if column != 1:
        return

    result = values[0]
    color = PREVIEW_RESULT_COLORS.get(result)

    if color is None:
        return

    item.setForeground(QColor("#ffffff"))
    item.setBackground(QColor(color))
