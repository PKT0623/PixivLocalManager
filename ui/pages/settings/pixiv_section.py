from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
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

        self.test_phpsessid_button = QPushButton("테스트")

        cookie_layout.addWidget(self.phpsessid_input, 1)
        cookie_layout.addWidget(self.save_phpsessid_button)
        cookie_layout.addWidget(self.test_phpsessid_button)

        self.phpsessid_status_label = QLabel("저장된 PHPSESSID 없음")
        self.phpsessid_status_label.setObjectName("infoText")

        request_title_label = QLabel("요청 안정성")
        request_title_label.setObjectName("fieldLabel")

        request_layout = QGridLayout()
        request_layout.setHorizontalSpacing(10)
        request_layout.setVerticalSpacing(8)

        self.request_interval_min_input = self._create_int_input("3")
        self.request_interval_max_input = self._create_int_input("6")
        self.retry_count_input = self._create_int_input("2")
        self.retry_interval_input = self._create_int_input("5")

        request_layout.addWidget(QLabel("최소 요청 간격(초)"), 0, 0)
        request_layout.addWidget(self.request_interval_min_input, 0, 1)
        request_layout.addWidget(QLabel("최대 요청 간격(초)"), 0, 2)
        request_layout.addWidget(self.request_interval_max_input, 0, 3)

        request_layout.addWidget(QLabel("재시도 횟수"), 1, 0)
        request_layout.addWidget(self.retry_count_input, 1, 1)
        request_layout.addWidget(QLabel("재시도 간격(초)"), 1, 2)
        request_layout.addWidget(self.retry_interval_input, 1, 3)

        self.save_request_settings_button = QPushButton("요청 설정 저장")
        self.save_request_settings_button.setObjectName("primaryButton")

        layout.addWidget(title_label)
        layout.addWidget(cookie_label)
        layout.addLayout(cookie_layout)
        layout.addWidget(self.phpsessid_status_label)
        layout.addSpacing(6)
        layout.addWidget(request_title_label)
        layout.addLayout(request_layout)
        layout.addWidget(self.save_request_settings_button)

    def _create_int_input(self, placeholder: str) -> QLineEdit:
        input_widget = QLineEdit()
        input_widget.setPlaceholderText(placeholder)
        input_widget.setValidator(QIntValidator(0, 999))
        return input_widget
