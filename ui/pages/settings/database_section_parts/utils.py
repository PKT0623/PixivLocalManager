from PySide6.QtWidgets import (
    QGridLayout,
    QLabel,
)


class DatabaseSectionUtilsMixin:
    def get_selected_backup_path(self) -> str | None:
        selected_rows = self.backup_table.selectionModel().selectedRows()

        if not selected_rows:
            return None

        row = selected_rows[0].row()
        item = self.backup_table.item(row, 0)

        if item is None:
            return None

        return item.data(self.BACKUP_PATH_ROLE)

    def _create_info_value(self) -> QLabel:
        label = QLabel("-")
        label.setObjectName("infoText")
        return label

    def _add_info_row(
        self,
        layout: QGridLayout,
        row: int,
        label_text: str,
        value_label: QLabel,
    ):
        label = QLabel(label_text)
        label.setObjectName("fieldLabel")

        layout.addWidget(label, row, 0)
        layout.addWidget(value_label, row, 1)

    def _format_backup_type(
        self,
        backup_type: str,
    ) -> str:
        labels = {
            "auto": "자동",
            "manual": "수동",
            "restore_safety": "복원 전 안전백업",
            "unknown": "기타",
        }

        return labels.get(
            backup_type,
            "기타",
        )
