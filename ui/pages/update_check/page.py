from PySide6.QtCore import Signal
from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import (
    QCheckBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.services.artist import ArtistService
from app.services.settings_service import SettingsService

from .actions import UpdateCheckActions
from .artist_table import UpdateArtistTable
from .log_table import UpdateLogTable
from .selection_actions import UpdateSelectionActions
from .styles import UPDATE_CHECK_PAGE_STYLES
from .worker_config import (
    DEFAULT_UPDATE_CHECK_BATCH_REST_MS,
    DEFAULT_UPDATE_CHECK_BATCH_SIZE,
    DEFAULT_UPDATE_CHECK_REQUEST_INTERVAL_MS,
)


class UpdateCheckPage(QWidget):
    update_finished = Signal()

    def __init__(self):
        super().__init__()

        self.artists = []
        self.failed_artist_ids = []
        self.worker_thread = None
        self.worker = None

        self.artist_service = ArtistService()
        self.settings_service = SettingsService()
        self.actions = UpdateCheckActions(self)
        self.selection_actions = UpdateSelectionActions(self)

        self._setup_ui()
        self._connect_signals()
        self.load_request_settings()
        self.load_artists()
        self.reset_summary()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 24)
        layout.setSpacing(14)

        title_label = QLabel("업데이트 확인")
        title_label.setObjectName("pageTitle")

        self.option_frame = self._create_option_frame()
        self.summary_frame = self._create_summary_frame()
        self.progress_frame = self._create_progress_frame()
        self.table_frame = self._create_table_frame()
        self.log_frame = self._create_log_frame()

        self.status_label = QLabel("")
        self.status_label.setObjectName("statusLabel")

        layout.addWidget(title_label)
        layout.addWidget(self.option_frame)
        layout.addWidget(self.summary_frame)
        layout.addWidget(self.progress_frame)
        layout.addWidget(self.table_frame, 5)
        layout.addWidget(self.log_frame, 2)
        layout.addWidget(self.status_label)

        self.setStyleSheet(UPDATE_CHECK_PAGE_STYLES)

    def _create_option_frame(self) -> QFrame:
        option_frame = QFrame()
        option_frame.setObjectName("optionFrame")

        option_layout = QVBoxLayout(option_frame)
        option_layout.setContentsMargins(14, 14, 14, 14)
        option_layout.setSpacing(10)

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

        option_layout.addLayout(selection_layout)
        option_layout.addLayout(request_layout)

        return option_frame

    def _create_int_input(self, placeholder: str) -> QLineEdit:
        input_widget = QLineEdit()
        input_widget.setPlaceholderText(placeholder)
        input_widget.setValidator(QIntValidator(0, 999999))
        input_widget.setFixedWidth(100)

        return input_widget

    def _create_summary_frame(self) -> QFrame:
        summary_frame = QFrame()
        summary_frame.setObjectName("summaryFrame")

        frame_layout = QVBoxLayout(summary_frame)
        frame_layout.setContentsMargins(14, 12, 14, 14)
        frame_layout.setSpacing(8)

        title_label = QLabel("결과 요약")
        title_label.setObjectName("sectionTitle")

        summary_layout = QHBoxLayout()
        summary_layout.setSpacing(10)

        self.summary_total_label = self._create_summary_item(
            summary_layout,
            "총 확인",
        )
        self.summary_latest_label = self._create_summary_item(
            summary_layout,
            "최신",
        )
        self.summary_need_update_label = self._create_summary_item(
            summary_layout,
            "업데이트 필요",
        )
        self.summary_error_label = self._create_summary_item(
            summary_layout,
            "오류",
        )
        self.summary_skipped_label = self._create_summary_item(
            summary_layout,
            "스킵",
        )
        self.summary_missing_label = self._create_summary_item(
            summary_layout,
            "누락 합계",
        )

        frame_layout.addWidget(title_label)
        frame_layout.addLayout(summary_layout)

        return summary_frame

    def _create_summary_item(
        self,
        parent_layout: QHBoxLayout,
        title: str,
    ) -> QLabel:
        item_frame = QFrame()
        item_frame.setObjectName("summaryItemFrame")

        item_layout = QVBoxLayout(item_frame)
        item_layout.setContentsMargins(14, 10, 14, 10)
        item_layout.setSpacing(4)

        value_label = QLabel("0")
        value_label.setObjectName("summaryValueLabel")

        title_label = QLabel(title)
        title_label.setObjectName("summaryTextLabel")

        item_layout.addWidget(value_label)
        item_layout.addWidget(title_label)

        parent_layout.addWidget(item_frame, 1)

        return value_label

    def _create_progress_frame(self) -> QFrame:
        progress_frame = QFrame()
        progress_frame.setObjectName("progressFrame")

        frame_layout = QVBoxLayout(progress_frame)
        frame_layout.setContentsMargins(14, 12, 14, 12)
        frame_layout.setSpacing(8)

        title_label = QLabel("실행")
        title_label.setObjectName("sectionTitle")

        progress_layout = QHBoxLayout()
        progress_layout.setSpacing(10)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("0 / 0")

        self.start_button = QPushButton("시작")
        self.start_button.setObjectName("primaryButton")

        self.pause_button = QPushButton("일시정지")
        self.pause_button.setEnabled(False)

        self.resume_button = QPushButton("재개")
        self.resume_button.setEnabled(False)

        self.cancel_button = QPushButton("중지")
        self.cancel_button.setEnabled(False)

        self.export_csv_button = QPushButton("CSV 저장")
        self.export_csv_button.setEnabled(False)

        progress_layout.addWidget(self.progress_bar, 1)
        progress_layout.addWidget(self.start_button)
        progress_layout.addWidget(self.pause_button)
        progress_layout.addWidget(self.resume_button)
        progress_layout.addWidget(self.cancel_button)
        progress_layout.addWidget(self.export_csv_button)

        frame_layout.addWidget(title_label)
        frame_layout.addLayout(progress_layout)

        return progress_frame

    def _create_table_frame(self) -> QFrame:
        table_frame = QFrame()
        table_frame.setObjectName("tableFrame")

        frame_layout = QVBoxLayout(table_frame)
        frame_layout.setContentsMargins(14, 12, 14, 14)
        frame_layout.setSpacing(8)

        title_label = QLabel("작가 목록")
        title_label.setObjectName("sectionTitle")

        self.artist_table = UpdateArtistTable()

        frame_layout.addWidget(title_label)
        frame_layout.addWidget(self.artist_table, 1)

        return table_frame

    def _create_log_frame(self) -> QFrame:
        log_frame = QFrame()
        log_frame.setObjectName("logFrame")

        frame_layout = QVBoxLayout(log_frame)
        frame_layout.setContentsMargins(14, 12, 14, 14)
        frame_layout.setSpacing(8)

        title_label = QLabel("결과 로그")
        title_label.setObjectName("sectionTitle")

        self.log_table = UpdateLogTable()

        frame_layout.addWidget(title_label)
        frame_layout.addWidget(self.log_table, 1)

        return log_frame

    def _connect_signals(self):
        self.select_all_button.clicked.connect(
            self.selection_actions.select_all
        )
        self.clear_selection_button.clicked.connect(
            self.selection_actions.clear_selection
        )
        self.select_unknown_button.clicked.connect(
            self.selection_actions.select_unknown
        )
        self.select_need_update_button.clicked.connect(
            self.selection_actions.select_need_update
        )
        self.select_failed_button.clicked.connect(
            self.selection_actions.select_failed
        )
        self.test_phpsessid_button.clicked.connect(
            self.actions.test_phpsessid
        )
        self.start_button.clicked.connect(
            self.actions.start_update_check
        )
        self.pause_button.clicked.connect(
            self.actions.pause_update_check
        )
        self.resume_button.clicked.connect(
            self.actions.resume_update_check
        )
        self.cancel_button.clicked.connect(
            self.actions.cancel_update_check
        )
        self.export_csv_button.clicked.connect(
            self.actions.export_log_csv
        )
        self.skip_recent_checkbox.toggled.connect(
            self.update_target_count
        )
        self.artist_table.selection_changed.connect(
            self.update_target_count
        )

    def load_request_settings(self):
        self.request_interval_ms_input.setText(
            str(
                self.settings_service.get_int_setting(
                    "update_check_request_interval_ms",
                    DEFAULT_UPDATE_CHECK_REQUEST_INTERVAL_MS,
                )
            )
        )
        self.batch_size_input.setText(
            str(
                self.settings_service.get_int_setting(
                    "update_check_batch_size",
                    DEFAULT_UPDATE_CHECK_BATCH_SIZE,
                )
            )
        )
        self.batch_rest_ms_input.setText(
            str(
                self.settings_service.get_int_setting(
                    "update_check_batch_rest_ms",
                    DEFAULT_UPDATE_CHECK_BATCH_REST_MS,
                )
            )
        )

    def get_request_interval_ms(self) -> int:
        return self._read_int(
            self.request_interval_ms_input.text(),
            DEFAULT_UPDATE_CHECK_REQUEST_INTERVAL_MS,
        )

    def get_batch_size(self) -> int:
        return self._read_int(
            self.batch_size_input.text(),
            DEFAULT_UPDATE_CHECK_BATCH_SIZE,
        )

    def get_batch_rest_ms(self) -> int:
        return self._read_int(
            self.batch_rest_ms_input.text(),
            DEFAULT_UPDATE_CHECK_BATCH_REST_MS,
        )

    def _read_int(
        self,
        value: str,
        default: int,
    ) -> int:
        try:
            return max(0, int(value))
        except (TypeError, ValueError):
            return default

    def load_artists(self):
        self.artists = self.artist_service.get_all_artists()
        self.artist_table.load_artists(self.artists)
        self.update_target_count()

    def update_target_count(self):
        artist_ids = self.selection_actions.get_selected_artist_ids()
        count = len(artist_ids)

        self.target_count_label.setText(f"확인 대상: {count}명")

        if count == 0:
            self.status_label.setText("")
        else:
            self.status_label.setText(f"업데이트 확인 대상: {count}명")

    def reset_summary(self):
        self.update_summary(
            {
                "total": 0,
                "latest": 0,
                "need_update": 0,
                "error": 0,
                "skipped": 0,
                "missing": 0,
            }
        )

    def update_summary(self, summary: dict):
        self.summary_total_label.setText(str(summary.get("total", 0)))
        self.summary_latest_label.setText(str(summary.get("latest", 0)))
        self.summary_need_update_label.setText(
            str(summary.get("need_update", 0))
        )
        self.summary_error_label.setText(str(summary.get("error", 0)))
        self.summary_skipped_label.setText(str(summary.get("skipped", 0)))
        self.summary_missing_label.setText(str(summary.get("missing", 0)))

    def shutdown_worker(self):
        self.actions.shutdown_worker()
