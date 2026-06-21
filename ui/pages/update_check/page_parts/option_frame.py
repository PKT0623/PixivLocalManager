from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import (
    QCheckBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

from ..worker_config import (
    DEFAULT_UPDATE_CHECK_BATCH_REST_MS,
    DEFAULT_UPDATE_CHECK_BATCH_SIZE,
    DEFAULT_UPDATE_CHECK_REQUEST_INTERVAL_MS,
)


class UpdateCheckOptionFrameMixin:
    def _create_option_frame(self) -> QFrame:
        option_frame = QFrame()
        option_frame.setObjectName("optionFrame")

        option_layout = QVBoxLayout(option_frame)
        option_layout.setContentsMargins(14, 14, 14, 14)
        option_layout.setSpacing(10)

        selection_layout = self._create_selection_layout()
        request_layout = self._create_request_layout()

        option_layout.addLayout(selection_layout)
        option_layout.addLayout(request_layout)

        return option_frame

    def _create_selection_layout(self) -> QHBoxLayout:
        selection_layout = QHBoxLayout()
        selection_layout.setSpacing(10)

        self.target_count_label = QLabel("확인 대상: 0명")
        self.target_count_label.setObjectName("targetCountLabel")

        self.select_all_button = QPushButton("전체 선택")
        self.clear_selection_button = QPushButton("전체 해제")
        self.select_unknown_button = QPushButton("미확인 선택")
        self.select_need_update_button = QPushButton("업데이트 필요 선택")
        self.select_failed_button = QPushButton("실패 작가 선택")
        self.test_phpsessid_button = QPushButton("PHPSESSID 테스트")

        self.skip_recent_checkbox = QCheckBox(
            "최근 1일 이내 확인한 작가 제외"
        )
        self.skip_recent_checkbox.setChecked(False)

        selection_layout.addWidget(self.target_count_label)
        selection_layout.addSpacing(8)
        selection_layout.addWidget(self.select_all_button)
        selection_layout.addWidget(self.clear_selection_button)
        selection_layout.addWidget(self.select_unknown_button)
        selection_layout.addWidget(self.select_need_update_button)
        selection_layout.addWidget(self.select_failed_button)
        selection_layout.addStretch()
        selection_layout.addWidget(self.skip_recent_checkbox)
        selection_layout.addWidget(self.test_phpsessid_button)

        return selection_layout

    def _create_request_layout(self) -> QGridLayout:
        request_layout = QGridLayout()
        request_layout.setHorizontalSpacing(10)
        request_layout.setVerticalSpacing(8)

        self.request_interval_ms_input = self._create_int_input(
            str(DEFAULT_UPDATE_CHECK_REQUEST_INTERVAL_MS)
        )
        self.batch_size_input = self._create_int_input(
            str(DEFAULT_UPDATE_CHECK_BATCH_SIZE)
        )
        self.batch_rest_ms_input = self._create_int_input(
            str(DEFAULT_UPDATE_CHECK_BATCH_REST_MS)
        )

        request_layout.addWidget(QLabel("요청 간격(ms)"), 0, 0)
        request_layout.addWidget(self.request_interval_ms_input, 0, 1)
        request_layout.addWidget(QLabel("배치 작가 수"), 0, 2)
        request_layout.addWidget(self.batch_size_input, 0, 3)
        request_layout.addWidget(QLabel("배치 휴식(ms)"), 0, 4)
        request_layout.addWidget(self.batch_rest_ms_input, 0, 5)
        request_layout.setColumnStretch(6, 1)

        return request_layout

    def _create_int_input(self, placeholder: str) -> QLineEdit:
        input_widget = QLineEdit()
        input_widget.setPlaceholderText(placeholder)
        input_widget.setValidator(QIntValidator(0, 999999))
        input_widget.setFixedWidth(100)

        return input_widget
