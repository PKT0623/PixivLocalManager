from PySide6.QtCore import Signal
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from app.services.settings_service import SettingsService

from .actions import ScanActions
from .folder_section import ScanFolderSection
from .log_table import ScanLogTable
from .page_parts import (
    ScanLogHeaderMixin,
    ScanPreviewHeaderMixin,
    ScanSignalConnectorMixin,
)
from .preview_table import ScanPreviewTable
from .progress_section import ScanProgressSection
from .scan_styles import SCAN_PAGE_STYLES


class ScanPage(
    QWidget,
    ScanPreviewHeaderMixin,
    ScanLogHeaderMixin,
    ScanSignalConnectorMixin,
):
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

        self.folder_section = ScanFolderSection()
        self.progress_section = ScanProgressSection()
        self.folder_section.layout().addWidget(self.progress_section)

        self._setup_preview_header()
        self.preview_table = ScanPreviewTable()

        self._setup_log_header()
        self.log_table = ScanLogTable()

        layout.addWidget(title_label)
        layout.addWidget(self.folder_section)
        layout.addLayout(self.preview_header_layout)
        layout.addWidget(self.preview_table, 1)
        layout.addLayout(self.log_header_layout)
        layout.addWidget(self.log_table, 1)

        self.setStyleSheet(SCAN_PAGE_STYLES)
