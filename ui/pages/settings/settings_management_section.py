from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)


class SettingsManagementSection(QFrame):
    def __init__(self):
        super().__init__()

        self.setObjectName("settingFrame")
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        title_label = QLabel("설정 관리 / 사용자 환경")
        title_label.setObjectName("sectionTitle")

        action_layout = QHBoxLayout()
        action_layout.setSpacing(8)

        self.backup_settings_button = QPushButton("설정 백업")
        self.restore_settings_button = QPushButton("설정 복원")
        self.reset_settings_button = QPushButton("설정 초기화")
        self.reset_settings_button.setObjectName("dangerButton")

        action_layout.addWidget(self.backup_settings_button)
        action_layout.addWidget(self.restore_settings_button)
        action_layout.addWidget(self.reset_settings_button)
        action_layout.addStretch()

        info_layout = QGridLayout()
        info_layout.setHorizontalSpacing(16)
        info_layout.setVerticalSpacing(8)

        self.window_size_value = self._create_info_value()
        self.window_position_value = self._create_info_value()
        self.last_backup_folder_value = self._create_info_value()
        self.last_restore_folder_value = self._create_info_value()
        self.last_export_folder_value = self._create_info_value()

        self._add_info_row(
            info_layout,
            0,
            "저장된 창 크기",
            self.window_size_value,
        )
        self._add_info_row(
            info_layout,
            1,
            "저장된 창 위치",
            self.window_position_value,
        )
        self._add_info_row(
            info_layout,
            2,
            "마지막 백업 경로",
            self.last_backup_folder_value,
        )
        self._add_info_row(
            info_layout,
            3,
            "마지막 복원 경로",
            self.last_restore_folder_value,
        )
        self._add_info_row(
            info_layout,
            4,
            "마지막 내보내기 경로",
            self.last_export_folder_value,
        )

        guide_label = QLabel(
            "창 크기와 위치는 프로그램 종료 시 자동 저장되고 다음 실행 시 복원됩니다."
        )
        guide_label.setObjectName("infoText")

        layout.addWidget(title_label)
        layout.addLayout(action_layout)
        layout.addLayout(info_layout)
        layout.addWidget(guide_label)
        layout.addStretch()

    def update_environment_info(
        self,
        info: dict,
    ):
        self.window_size_value.setText(info.get("window_size", "-"))
        self.window_position_value.setText(info.get("window_position", "-"))
        self.last_backup_folder_value.setText(
            info.get("last_backup_folder", "-")
        )
        self.last_restore_folder_value.setText(
            info.get("last_restore_folder", "-")
        )
        self.last_export_folder_value.setText(
            info.get("last_export_folder", "-")
        )

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
