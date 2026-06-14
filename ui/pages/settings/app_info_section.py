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

        app_name_label = QLabel("프로그램")
        app_name_label.setObjectName("fieldLabel")

        app_name_value = QLabel("Pixiv Local Manager")
        app_name_value.setObjectName("infoText")

        version_label = QLabel("버전")
        version_label.setObjectName("fieldLabel")

        version_value = QLabel("0.1.0")
        version_value.setObjectName("infoText")

        stack_label = QLabel("기술 스택")
        stack_label.setObjectName("fieldLabel")

        stack_value = QLabel("Python / PySide6 / SQLite")
        stack_value.setObjectName("infoText")

        layout.addWidget(title_label, 0, 0, 1, 2)
        layout.addWidget(app_name_label, 1, 0)
        layout.addWidget(app_name_value, 1, 1)
        layout.addWidget(version_label, 2, 0)
        layout.addWidget(version_value, 2, 1)
        layout.addWidget(stack_label, 3, 0)
        layout.addWidget(stack_value, 3, 1)
