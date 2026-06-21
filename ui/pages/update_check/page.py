from PySide6.QtCore import Signal
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from app.services.artist import ArtistService
from app.services.settings_service import SettingsService

from .actions import UpdateCheckActions
from .page_parts import (
    UpdateCheckDataMixin,
    UpdateCheckLogFrameMixin,
    UpdateCheckOptionFrameMixin,
    UpdateCheckProgressFrameMixin,
    UpdateCheckSettingsMixin,
    UpdateCheckSummaryFrameMixin,
    UpdateCheckTableFrameMixin,
)
from .selection_actions import UpdateSelectionActions
from .styles import UPDATE_CHECK_PAGE_STYLES


class UpdateCheckPage(
    QWidget,
    UpdateCheckOptionFrameMixin,
    UpdateCheckSummaryFrameMixin,
    UpdateCheckProgressFrameMixin,
    UpdateCheckTableFrameMixin,
    UpdateCheckLogFrameMixin,
    UpdateCheckSettingsMixin,
    UpdateCheckDataMixin,
):
    update_finished = Signal()
    artist_detail_requested = Signal(int)
    artist_list_requested = Signal(list)

    worker_log_received = Signal(dict)
    worker_progress_received = Signal(int, int)
    worker_summary_received = Signal(dict)
    worker_failed_artist_received = Signal(int)
    worker_paused_received = Signal(int, int)
    worker_finished_received = Signal()
    worker_failed_received = Signal(str)

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
        self.open_log_artist_detail_button.clicked.connect(
            self.actions.open_selected_log_artist_detail
        )
        self.open_log_artist_list_button.clicked.connect(
            self.actions.open_selected_log_artist_list
        )
        self.rescan_selected_log_button.clicked.connect(
            self.actions.rescan_selected_log_artists
        )
        self.rescan_missing_log_button.clicked.connect(
            self.actions.rescan_missing_log_artists
        )
        self.rescan_error_log_button.clicked.connect(
            self.actions.rescan_error_log_artists
        )
        self.export_download_txt_button.clicked.connect(
            self.actions.export_download_plan_txt
        )
        self.export_download_csv_button.clicked.connect(
            self.actions.export_download_plan_csv
        )
        self.skip_recent_checkbox.toggled.connect(
            self.update_target_count
        )
        self.artist_table.selection_changed.connect(
            self.update_target_count
        )
        self.log_table.artist_detail_requested.connect(
            self.actions.open_log_artist_detail_by_id
        )
        self.log_table.selection_changed.connect(
            self.actions.update_log_action_buttons
        )

        self.worker_log_received.connect(
            self.actions.handle_log_requested
        )
        self.worker_progress_received.connect(
            self.actions.update_progress
        )
        self.worker_summary_received.connect(
            self.actions.handle_summary_updated
        )
        self.worker_failed_artist_received.connect(
            self.actions.add_failed_artist_id
        )
        self.worker_paused_received.connect(
            self.actions.handle_paused
        )
        self.worker_finished_received.connect(
            self.actions.handle_finished
        )
        self.worker_failed_received.connect(
            self.actions.handle_failed
        )
