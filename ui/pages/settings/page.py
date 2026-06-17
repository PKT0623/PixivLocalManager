from PySide6.QtWidgets import (
    QLabel,
    QVBoxLayout,
    QWidget,
)

from app.services.artist import ArtistService
from app.services.settings_service import SettingsService

from .actions import SettingsActions
from .app_info_section import AppInfoSection
from .database_section import DatabaseSection
from .folder_section import FolderSection
from .pixiv_section import PixivSection
from .settings_styles import SETTINGS_PAGE_STYLE


class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()

        self.settings_service = SettingsService()
        self.artist_service = ArtistService()
        self.actions = SettingsActions(self)

        self._setup_ui()
        self._connect_signals()
        self.actions.load_settings()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(16)

        title_label = QLabel("설정")
        title_label.setObjectName("pageTitle")

        description_label = QLabel(
            "DB 경로, 백업, 내보내기 같은 프로그램 설정을 관리하는 화면입니다."
        )
        description_label.setObjectName("pageDescription")

        self.folder_section = FolderSection()
        self.pixiv_section = PixivSection()
        self.database_section = DatabaseSection()
        self.app_info_section = AppInfoSection()

        self.status_label = QLabel("준비됨")
        self.status_label.setObjectName("statusLabel")

        layout.addWidget(title_label)
        layout.addWidget(description_label)
        layout.addWidget(self.folder_section)
        layout.addWidget(self.pixiv_section)
        layout.addWidget(self.database_section)
        layout.addWidget(self.app_info_section)
        layout.addWidget(self.status_label)
        layout.addStretch()

        self.setStyleSheet(SETTINGS_PAGE_STYLE)

    def _connect_signals(self):
        self.folder_section.select_pixiv_root_button.clicked.connect(
            self.actions.select_pixiv_root_folder
        )
        self.folder_section.save_pixiv_root_button.clicked.connect(
            self.actions.save_pixiv_root_folder
        )
        self.pixiv_section.save_phpsessid_button.clicked.connect(
            self.actions.save_phpsessid
        )
        self.pixiv_section.test_phpsessid_button.clicked.connect(
            self.actions.test_phpsessid
        )
        self.pixiv_section.save_request_settings_button.clicked.connect(
            self.actions.save_pixiv_request_settings
        )
        self.database_section.open_db_folder_button.clicked.connect(
            self.actions.open_db_folder
        )
        self.database_section.backup_db_button.clicked.connect(
            self.actions.backup_database
        )
        self.database_section.restore_db_button.clicked.connect(
            self.actions.restore_database
        )
        self.database_section.export_csv_button.clicked.connect(
            self.actions.export_artists_csv
        )
