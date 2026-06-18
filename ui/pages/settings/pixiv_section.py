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

        self.session_status_label = QLabel("세션 상태: 미확인")
        self.session_status_label.setObjectName("infoText")

        layout.addWidget(title_label)
        layout.addWidget(cookie_label)
        layout.addLayout(cookie_layout)
        layout.addWidget(self.phpsessid_status_label)
        layout.addWidget(self.session_status_label)


class PixivManagerRequestSection(QFrame):
    def __init__(self):
        super().__init__()

        self.setObjectName("settingFrame")
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title_label = QLabel("Pixiv 관리 요청")
        title_label.setObjectName("sectionTitle")

        description_label = QLabel(
            "Pixiv 관리의 팔로우/북마크 메타데이터 동기화 요청 설정입니다."
        )
        description_label.setObjectName("infoText")

        request_layout = QGridLayout()
        request_layout.setHorizontalSpacing(10)
        request_layout.setVerticalSpacing(8)

        self.request_interval_ms_input = self._create_int_input("2000")
        self.batch_size_input = self._create_int_input("1000")
        self.batch_rest_ms_input = self._create_int_input("300000")
        self.retry_count_input = self._create_int_input("3")

        request_layout.addWidget(QLabel("요청 간격(ms)"), 0, 0)
        request_layout.addWidget(self.request_interval_ms_input, 0, 1)
        request_layout.addWidget(QLabel("배치 요청 수"), 0, 2)
        request_layout.addWidget(self.batch_size_input, 0, 3)

        request_layout.addWidget(QLabel("배치 휴식(ms)"), 1, 0)
        request_layout.addWidget(self.batch_rest_ms_input, 1, 1)
        request_layout.addWidget(QLabel("재시도 횟수"), 1, 2)
        request_layout.addWidget(self.retry_count_input, 1, 3)

        self.save_request_settings_button = QPushButton("Pixiv 관리 요청 저장")
        self.save_request_settings_button.setObjectName("primaryButton")

        layout.addWidget(title_label)
        layout.addWidget(description_label)
        layout.addLayout(request_layout)
        layout.addWidget(self.save_request_settings_button)

    def _create_int_input(self, placeholder: str) -> QLineEdit:
        input_widget = QLineEdit()
        input_widget.setPlaceholderText(placeholder)
        input_widget.setValidator(QIntValidator(0, 999999))
        return input_widget


class UpdateCheckRequestSection(QFrame):
    def __init__(self):
        super().__init__()

        self.setObjectName("settingFrame")
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title_label = QLabel("업데이트 확인 요청")
        title_label.setObjectName("sectionTitle")

        description_label = QLabel(
            "업데이트 확인의 작가별 Pixiv 요청 간격과 배치 휴식 설정입니다."
        )
        description_label.setObjectName("infoText")

        request_layout = QGridLayout()
        request_layout.setHorizontalSpacing(10)
        request_layout.setVerticalSpacing(8)

        self.request_interval_ms_input = self._create_int_input("1000")
        self.batch_size_input = self._create_int_input("20")
        self.batch_rest_ms_input = self._create_int_input("180000")

        request_layout.addWidget(QLabel("요청 간격(ms)"), 0, 0)
        request_layout.addWidget(self.request_interval_ms_input, 0, 1)
        request_layout.addWidget(QLabel("배치 작가 수"), 0, 2)
        request_layout.addWidget(self.batch_size_input, 0, 3)

        request_layout.addWidget(QLabel("배치 휴식(ms)"), 1, 0)
        request_layout.addWidget(self.batch_rest_ms_input, 1, 1)

        self.save_request_settings_button = QPushButton("업데이트 확인 요청 저장")
        self.save_request_settings_button.setObjectName("primaryButton")

        layout.addWidget(title_label)
        layout.addWidget(description_label)
        layout.addLayout(request_layout)
        layout.addWidget(self.save_request_settings_button)

    def _create_int_input(self, placeholder: str) -> QLineEdit:
        input_widget = QLineEdit()
        input_widget.setPlaceholderText(placeholder)
        input_widget.setValidator(QIntValidator(0, 999999))
        return input_widget
