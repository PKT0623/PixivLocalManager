from PySide6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
)


class DatabaseBackupSectionMixin:
    def _create_backup_section(self):
        auto_backup_title = QLabel("자동 백업")
        auto_backup_title.setObjectName("fieldLabel")

        auto_backup_layout = QHBoxLayout()
        auto_backup_layout.setSpacing(8)

        self.auto_backup_enabled_checkbox = QCheckBox("자동 백업 사용")

        self.backup_interval_input = QSpinBox()
        self.backup_interval_input.setRange(1, 365)
        self.backup_interval_input.setSuffix(" 일")
        self.backup_interval_input.setFixedWidth(100)

        self.backup_keep_count_input = QSpinBox()
        self.backup_keep_count_input.setRange(1, 999)
        self.backup_keep_count_input.setSuffix(" 개")
        self.backup_keep_count_input.setFixedWidth(100)

        self.save_backup_settings_button = QPushButton("백업 설정 저장")
        self.save_backup_settings_button.setObjectName("primaryButton")

        auto_backup_layout.addWidget(self.auto_backup_enabled_checkbox)
        auto_backup_layout.addWidget(QLabel("주기"))
        auto_backup_layout.addWidget(self.backup_interval_input)
        auto_backup_layout.addWidget(QLabel("보관"))
        auto_backup_layout.addWidget(self.backup_keep_count_input)
        auto_backup_layout.addWidget(self.save_backup_settings_button)
        auto_backup_layout.addStretch()

        self.backup_info_label = QLabel("최근 백업: - / 총 백업 용량: -")
        self.backup_info_label.setObjectName("infoText")

        backup_action_layout = QHBoxLayout()
        backup_action_layout.setSpacing(8)

        self.backup_db_button = QPushButton("DB 백업 생성")
        self.restore_db_button = QPushButton("선택 백업 복원")
        self.delete_backup_button = QPushButton("선택 백업 삭제")
        self.refresh_backup_button = QPushButton("목록 새로고침")
        self.open_backup_folder_button = QPushButton("백업 폴더 열기")
        self.export_csv_button = QPushButton("CSV 내보내기")

        backup_action_layout.addWidget(self.backup_db_button)
        backup_action_layout.addWidget(self.restore_db_button)
        backup_action_layout.addWidget(self.delete_backup_button)
        backup_action_layout.addWidget(self.refresh_backup_button)
        backup_action_layout.addWidget(self.open_backup_folder_button)
        backup_action_layout.addWidget(self.export_csv_button)
        backup_action_layout.addStretch()

        return (
            auto_backup_title,
            auto_backup_layout,
            self.backup_info_label,
            backup_action_layout,
        )
