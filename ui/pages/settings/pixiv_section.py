from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)


class PixivSection(QFrame):
    def __init__(self):
        super().__init__()

        self.setObjectName("settingFrame")
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title_label = QLabel("Pixiv 연동")
        title_label.setObjectName("sectionTitle")

        cookie_label = QLabel("PHPSESSID")
        cookie_label.setObjectName("fieldLabel")

        cookie_layout = QHBoxLayout()
        cookie_layout.setSpacing(8)

        self.phpsessid_input = QLineEdit()
        self.phpsessid_input.setEchoMode(QLineEdit.Password)
        self.phpsessid_input.setPlaceholderText("Pixiv PHPSESSID를 입력하세요.")

        self.save_phpsessid_button = QPushButton("저장")
        self.save_phpsessid_button.setObjectName("primaryButton")

        cookie_layout.addWidget(self.phpsessid_input, 1)
        cookie_layout.addWidget(self.save_phpsessid_button)

        self.phpsessid_status_label = QLabel("저장된 PHPSESSID 없음")
        self.phpsessid_status_label.setObjectName("infoText")

        layout.addWidget(title_label)
        layout.addWidget(cookie_label)
        layout.addLayout(cookie_layout)
        layout.addWidget(self.phpsessid_status_label)
