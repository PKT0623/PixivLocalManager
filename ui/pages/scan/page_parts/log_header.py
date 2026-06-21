from PySide6.QtWidgets import QCheckBox, QComboBox, QHBoxLayout, QLabel, QPushButton


class ScanLogHeaderMixin:
    def _setup_log_header(self):
        self.log_header_layout = QHBoxLayout()

        log_label = QLabel("결과 로그")
        log_label.setObjectName("sectionTitle")

        self.result_filter_combo = QComboBox()
        self.result_filter_combo.addItems(
            [
                "전체",
                "등록",
                "업데이트",
                "변경 없음",
                "경고",
                "오류",
                "제외",
                "실패",
            ]
        )

        self.error_only_checkbox = QCheckBox("오류 로그만 보기")

        self.retry_failed_button = QPushButton("실패 재시도")
        self.clear_failed_button = QPushButton("실패 초기화")
        self.export_failed_csv_button = QPushButton("실패 CSV")
        self.export_all_csv_button = QPushButton("결과 CSV")
        self.clear_log_button = QPushButton("로그 지우기")

        self._setup_log_button_styles()
        self._add_log_header_widgets(log_label)

    def _setup_log_button_styles(self):
        buttons = (
            self.retry_failed_button,
            self.clear_failed_button,
            self.export_failed_csv_button,
            self.export_all_csv_button,
            self.clear_log_button,
        )

        for button in buttons:
            button.setObjectName("clearLogButton")

    def _add_log_header_widgets(
        self,
        log_label: QLabel,
    ):
        self.log_header_layout.addWidget(log_label)
        self.log_header_layout.addStretch()
        self.log_header_layout.addWidget(self.result_filter_combo)
        self.log_header_layout.addWidget(self.error_only_checkbox)
        self.log_header_layout.addWidget(self.retry_failed_button)
        self.log_header_layout.addWidget(self.clear_failed_button)
        self.log_header_layout.addWidget(self.export_failed_csv_button)
        self.log_header_layout.addWidget(self.export_all_csv_button)
        self.log_header_layout.addWidget(self.clear_log_button)
