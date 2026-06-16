from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.services.settings_service import SettingsService

from .actions import ScanActions
from .folder_section import ScanFolderSection
from .log_table import ScanLogTable
from .preview_table import ScanPreviewTable
from .progress_section import ScanProgressSection
from .scan_styles import SCAN_PAGE_STYLES


class ScanPage(QWidget):
    artist_detail_requested = Signal(int)

    def __init__(self):
        super().__init__()

        self.scan_thread = None
        self.scan_worker = None
        self.settings_service = SettingsService()
        self.actions = ScanActions(self)

        self._setup_ui()
        self._connect_signals()
        self.actions.load_default_folder()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(16)

        title_label = QLabel("폴더 스캔")
        title_label.setObjectName("pageTitle")

        description_label = QLabel(
            "Pixiv 이미지 폴더를 선택하고 최대 3단계 하위 폴더까지 "
            "분석해 DB에 등록합니다."
        )
        description_label.setObjectName("pageDescription")

        self.folder_section = ScanFolderSection()
        self.progress_section = ScanProgressSection()
        self.folder_section.layout().addWidget(self.progress_section)

        self._setup_preview_header()
        self.preview_table = ScanPreviewTable()

        self._setup_log_header()
        self.log_table = ScanLogTable()

        layout.addWidget(title_label)
        layout.addWidget(description_label)
        layout.addWidget(self.folder_section)
        layout.addLayout(self.preview_header_layout)
        layout.addWidget(self.preview_table, 1)
        layout.addLayout(self.log_header_layout)
        layout.addWidget(self.log_table, 1)

        self.setStyleSheet(SCAN_PAGE_STYLES)

    def _setup_preview_header(self):
        self.preview_header_layout = QHBoxLayout()

        preview_label = QLabel("스캔 미리보기")
        preview_label.setObjectName("sectionTitle")

        self.preview_summary_label = QLabel(
            "신규 0 / 업데이트 0 / 변경 없음 0 / 오류 0 / 선택 0"
        )
        self.preview_summary_label.setObjectName("subText")

        self.preview_show_created_checkbox = QCheckBox("신규만 보기")
        self.preview_show_updated_checkbox = QCheckBox("업데이트만 보기")
        self.preview_show_error_checkbox = QCheckBox("오류만 보기")

        self.preview_hide_unchanged_checkbox = QCheckBox("변경 없음 숨김")
        self.preview_hide_unchanged_checkbox.setChecked(True)

        self.preview_select_all_button = QPushButton("전체 선택")
        self.preview_select_all_button.setObjectName("clearLogButton")

        self.preview_clear_selection_button = QPushButton("전체 해제")
        self.preview_clear_selection_button.setObjectName("clearLogButton")

        self.preview_exclude_selected_button = QPushButton("선택 제외")
        self.preview_exclude_selected_button.setObjectName("clearLogButton")

        self.preview_keep_selected_button = QPushButton("선택만 남김")
        self.preview_keep_selected_button.setObjectName("clearLogButton")

        self.preview_exclude_error_button = QPushButton("오류 제외")
        self.preview_exclude_error_button.setObjectName("clearLogButton")

        self.preview_export_csv_button = QPushButton("미리보기 CSV")
        self.preview_export_csv_button.setObjectName("clearLogButton")

        self.preview_scan_selected_button = QPushButton("선택 항목 등록")
        self.preview_scan_selected_button.setObjectName("scanButton")

        self.preview_header_layout.addWidget(preview_label)
        self.preview_header_layout.addWidget(self.preview_summary_label)
        self.preview_header_layout.addStretch()
        self.preview_header_layout.addWidget(
            self.preview_show_created_checkbox
        )
        self.preview_header_layout.addWidget(
            self.preview_show_updated_checkbox
        )
        self.preview_header_layout.addWidget(
            self.preview_show_error_checkbox
        )
        self.preview_header_layout.addWidget(
            self.preview_hide_unchanged_checkbox
        )
        self.preview_header_layout.addWidget(
            self.preview_select_all_button
        )
        self.preview_header_layout.addWidget(
            self.preview_clear_selection_button
        )
        self.preview_header_layout.addWidget(
            self.preview_exclude_selected_button
        )
        self.preview_header_layout.addWidget(
            self.preview_keep_selected_button
        )
        self.preview_header_layout.addWidget(
            self.preview_exclude_error_button
        )
        self.preview_header_layout.addWidget(
            self.preview_export_csv_button
        )
        self.preview_header_layout.addWidget(
            self.preview_scan_selected_button
        )

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
        self.retry_failed_button.setObjectName("clearLogButton")

        self.clear_failed_button = QPushButton("실패 초기화")
        self.clear_failed_button.setObjectName("clearLogButton")

        self.export_failed_csv_button = QPushButton("실패 CSV")
        self.export_failed_csv_button.setObjectName("clearLogButton")

        self.export_all_csv_button = QPushButton("결과 CSV")
        self.export_all_csv_button.setObjectName("clearLogButton")

        self.clear_log_button = QPushButton("로그 지우기")
        self.clear_log_button.setObjectName("clearLogButton")

        self.log_header_layout.addWidget(log_label)
        self.log_header_layout.addStretch()
        self.log_header_layout.addWidget(self.result_filter_combo)
        self.log_header_layout.addWidget(self.error_only_checkbox)
        self.log_header_layout.addWidget(self.retry_failed_button)
        self.log_header_layout.addWidget(self.clear_failed_button)
        self.log_header_layout.addWidget(self.export_failed_csv_button)
        self.log_header_layout.addWidget(self.export_all_csv_button)
        self.log_header_layout.addWidget(self.clear_log_button)

    def _connect_signals(self):
        self.folder_section.folder_select_button.clicked.connect(
            self.actions.select_folder
        )
        self.folder_section.preview_button.clicked.connect(
            self.actions.start_preview
        )
        self.folder_section.scan_button.clicked.connect(
            self.actions.start_scan
        )
        self.folder_section.pause_button.clicked.connect(
            self.actions.pause_scan
        )
        self.folder_section.resume_button.clicked.connect(
            self.actions.resume_scan
        )
        self.folder_section.stop_button.clicked.connect(
            self.actions.stop_scan
        )
        self.preview_select_all_button.clicked.connect(
            self.preview_table.select_all_available
        )
        self.preview_clear_selection_button.clicked.connect(
            self.preview_table.clear_all_selection
        )
        self.preview_exclude_selected_button.clicked.connect(
            self.preview_table.exclude_selected_rows
        )
        self.preview_keep_selected_button.clicked.connect(
            self.preview_table.keep_selected_rows_only
        )
        self.preview_exclude_error_button.clicked.connect(
            self.preview_table.exclude_error_rows
        )
        self.preview_export_csv_button.clicked.connect(
            self.actions.export_preview_results_csv
        )
        self.preview_scan_selected_button.clicked.connect(
            self.actions.start_selected_preview_items_scan
        )
        self.preview_show_created_checkbox.toggled.connect(
            self.actions.apply_preview_filters
        )
        self.preview_show_updated_checkbox.toggled.connect(
            self.actions.apply_preview_filters
        )
        self.preview_show_error_checkbox.toggled.connect(
            self.actions.apply_preview_filters
        )
        self.preview_hide_unchanged_checkbox.toggled.connect(
            self.actions.apply_preview_filters
        )
        self.preview_table.selection_changed.connect(
            self._update_preview_summary
        )
        self.clear_log_button.clicked.connect(
            self.actions.clear_scan_results
        )
        self.result_filter_combo.currentTextChanged.connect(
            self.actions.apply_result_filter
        )
        self.error_only_checkbox.toggled.connect(
            self.actions.apply_error_only_filter
        )
        self.retry_failed_button.clicked.connect(
            self.actions.retry_failed_items
        )
        self.clear_failed_button.clicked.connect(
            self.actions.clear_failed_items
        )
        self.export_failed_csv_button.clicked.connect(
            self.actions.export_failed_items_csv
        )
        self.export_all_csv_button.clicked.connect(
            self.actions.export_all_scan_results_csv
        )
        self.log_table.artist_open_requested.connect(
            self.actions.open_artist_detail
        )
        self.log_table.folder_open_requested.connect(
            self.actions.open_folder
        )

    def _update_preview_summary(
        self,
        summary: dict,
    ):
        self.preview_summary_label.setText(
            "신규 "
            f"{summary.get('created', 0)} / "
            "업데이트 "
            f"{summary.get('updated', 0)} / "
            "변경 없음 "
            f"{summary.get('unchanged', 0)} / "
            "오류 "
            f"{summary.get('failed', 0)} / "
            "선택 "
            f"{summary.get('selected', 0)}"
        )
