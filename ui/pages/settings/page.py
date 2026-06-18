from PySide6.QtWidgets import (
    QLabel,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from app.services.artist import ArtistService
from app.services.settings_service import SettingsService

from .actions import SettingsActions
from .app_info_section import AppInfoSection
from .database_section import DatabaseSection
from .folder_section import FolderSection
from .pixiv_section import (
    PixivManagerRequestSection,
    PixivSection,
    UpdateCheckRequestSection,
)
from .settings_management_section import SettingsManagementSection
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
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(32, 32, 32, 32)
        root_layout.setSpacing(16)

        title_label = QLabel("설정")
        title_label.setObjectName("pageTitle")

        self.tab_widget = QTabWidget()
        self.tab_widget.setObjectName("settingsTabWidget")

        self.folder_section = FolderSection()
        self.pixiv_section = PixivSection()
        self.update_check_request_section = UpdateCheckRequestSection()
        self.pixiv_manager_request_section = PixivManagerRequestSection()
        self.database_section = DatabaseSection()
        self.settings_management_section = SettingsManagementSection()
        self.app_info_section = AppInfoSection()

        self.basic_tab = self._create_basic_tab()
        self.database_tab = self._create_database_tab()
        self.environment_tab = self._create_environment_tab()
        self.info_tab = self._create_info_tab()

        self.tab_widget.addTab(self.basic_tab, "기본 설정")
        self.tab_widget.addTab(self.database_tab, "데이터 관리")
        self.tab_widget.addTab(self.environment_tab, "환경 설정")
        self.tab_widget.addTab(self.info_tab, "프로그램 정보")

        self.status_label = QLabel("준비됨")
        self.status_label.setObjectName("statusLabel")

        root_layout.addWidget(title_label)
        root_layout.addWidget(self.tab_widget, 1)
        root_layout.addWidget(self.status_label)

        self.setStyleSheet(SETTINGS_PAGE_STYLE)

    def _create_basic_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 16, 0, 0)
        layout.setSpacing(16)

        layout.addWidget(self.folder_section)
        layout.addWidget(self.pixiv_section)
        layout.addWidget(self.update_check_request_section)
        layout.addWidget(self.pixiv_manager_request_section)
        layout.addStretch()

        return tab

    def _create_database_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 16, 0, 0)
        layout.setSpacing(16)

        layout.addWidget(self.database_section, 1)

        return tab

    def _create_environment_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 16, 0, 0)
        layout.setSpacing(16)

        layout.addWidget(self.settings_management_section, 1)

        return tab

    def _create_info_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 16, 0, 0)
        layout.setSpacing(16)

        layout.addWidget(self.app_info_section)
        layout.addStretch()

        return tab

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
        self.update_check_request_section.save_request_settings_button.clicked.connect(
            self.actions.save_update_check_request_settings
        )
        self.pixiv_manager_request_section.save_request_settings_button.clicked.connect(
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
        self.database_section.delete_backup_button.clicked.connect(
            self.actions.delete_selected_backup
        )
        self.database_section.refresh_backup_button.clicked.connect(
            self.actions.refresh_backup_list
        )
        self.database_section.open_backup_folder_button.clicked.connect(
            self.actions.open_backup_folder
        )
        self.database_section.save_backup_settings_button.clicked.connect(
            self.actions.save_backup_settings
        )
        self.database_section.export_csv_button.clicked.connect(
            self.actions.export_artists_csv
        )
        self.database_section.check_integrity_button.clicked.connect(
            self.actions.run_integrity_check
        )
        self.database_section.optimize_db_button.clicked.connect(
            self.actions.optimize_database
        )
        self.database_section.refresh_db_info_button.clicked.connect(
            self.actions.refresh_database_info
        )
        self.settings_management_section.backup_settings_button.clicked.connect(
            self.actions.backup_settings
        )
        self.settings_management_section.restore_settings_button.clicked.connect(
            self.actions.restore_settings
        )
        self.settings_management_section.reset_settings_button.clicked.connect(
            self.actions.reset_settings
        )
