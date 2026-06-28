from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QVBoxLayout,
)

from .database_section_parts import (
    DatabaseBackupSectionMixin,
    DatabaseBackupTableMixin,
    DatabaseInfoMixin,
    DatabaseSectionUtilsMixin,
)


class DatabaseSection(
    QFrame,
    DatabaseInfoMixin,
    DatabaseBackupSectionMixin,
    DatabaseBackupTableMixin,
    DatabaseSectionUtilsMixin,
):
    BACKUP_PATH_ROLE = Qt.UserRole + 1

    def __init__(self):
        super().__init__()

        self.setObjectName("settingFrame")
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        title_label = QLabel("데이터 관리")
        title_label.setObjectName("sectionTitle")

        (
            db_path_label,
            db_path_layout,
            db_info_grid,
            management_title,
            management_action_layout,
            integrity_result_text,
        ) = self._create_database_info_section()

        (
            auto_backup_title,
            auto_backup_layout,
            backup_info_label,
            backup_action_layout,
        ) = self._create_backup_section()

        backup_table = self._create_backup_table()

        layout.addWidget(title_label)
        layout.addWidget(db_path_label)
        layout.addLayout(db_path_layout)
        layout.addLayout(db_info_grid)
        layout.addWidget(management_title)
        layout.addLayout(management_action_layout)
        layout.addWidget(integrity_result_text)
        layout.addWidget(auto_backup_title)
        layout.addLayout(auto_backup_layout)
        layout.addWidget(backup_info_label)
        layout.addLayout(backup_action_layout)
        layout.addWidget(backup_table)
