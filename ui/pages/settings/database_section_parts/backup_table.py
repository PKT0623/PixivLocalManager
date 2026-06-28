from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QTableWidget,
    QTableWidgetItem,
)


class DatabaseBackupTableMixin:
    def _create_backup_table(self) -> QTableWidget:
        self.backup_table = QTableWidget()
        self.backup_table.setColumnCount(4)
        self.backup_table.setHorizontalHeaderLabels(
            [
                "파일명",
                "생성일",
                "크기",
                "종류",
            ]
        )
        self.backup_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.backup_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.backup_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.backup_table.verticalHeader().setVisible(False)
        self.backup_table.setAlternatingRowColors(True)
        self.backup_table.setMinimumHeight(220)

        header = self.backup_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)

        return self.backup_table

    def update_backup_table(
        self,
        backups: list,
    ):
        self.backup_table.setRowCount(0)

        for backup in backups:
            row = self.backup_table.rowCount()
            self.backup_table.insertRow(row)

            file_name_item = QTableWidgetItem(backup.file_name)
            file_name_item.setData(
                self.BACKUP_PATH_ROLE,
                backup.file_path,
            )

            created_at_item = QTableWidgetItem(backup.created_at)
            size_item = QTableWidgetItem(backup.size_label)
            type_item = QTableWidgetItem(
                self._format_backup_type(backup.backup_type)
            )

            for item in [
                file_name_item,
                created_at_item,
                size_item,
                type_item,
            ]:
                item.setTextAlignment(Qt.AlignCenter)

            file_name_item.setTextAlignment(
                Qt.AlignVCenter | Qt.AlignLeft
            )

            self.backup_table.setItem(row, 0, file_name_item)
            self.backup_table.setItem(row, 1, created_at_item)
            self.backup_table.setItem(row, 2, size_item)
            self.backup_table.setItem(row, 3, type_item)
