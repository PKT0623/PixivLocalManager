from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QLabel,
)


class AppInfoSection(QFrame):
    def __init__(self):
        super().__init__()

        self.setObjectName("settingFrame")
        self._setup_ui()

    def _setup_ui(self):
        layout = QGridLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setHorizontalSpacing(16)
        layout.setVerticalSpacing(8)

        title_label = QLabel("프로그램 정보")
        title_label.setObjectName("sectionTitle")

        self.app_name_value = self._create_info_value()
        self.version_value = self._create_info_value()
        self.stack_value = self._create_info_value()
        self.last_backup_value = self._create_info_value()
        self.backup_count_value = self._create_info_value()
        self.backup_total_size_value = self._create_info_value()

        layout.addWidget(title_label, 0, 0, 1, 2)
        self._add_info_row(layout, 1, "프로그램", self.app_name_value)
        self._add_info_row(layout, 2, "버전", self.version_value)
        self._add_info_row(layout, 3, "기술 스택", self.stack_value)
        self._add_info_row(layout, 4, "최근 백업", self.last_backup_value)
        self._add_info_row(layout, 5, "백업 개수", self.backup_count_value)
        self._add_info_row(
            layout,
            6,
            "전체 백업 용량",
            self.backup_total_size_value,
        )

    def update_program_info(
        self,
        info: dict,
    ):
        self.app_name_value.setText(info.get("app_name", "-"))
        self.version_value.setText(info.get("version", "-"))
        self.stack_value.setText(info.get("stack", "-"))
        self.last_backup_value.setText(info.get("last_backup_at", "-"))
        self.backup_count_value.setText(
            f"{info.get('backup_count', 0)}개"
        )
        self.backup_total_size_value.setText(
            info.get("backup_total_size", "-")
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
