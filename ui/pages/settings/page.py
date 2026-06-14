from PySide6.QtWidgets import (
    QLabel,
    QVBoxLayout,
    QWidget,
)

from app.services.artist_service import ArtistService
from app.services.settings_service import SettingsService

from .actions import SettingsActions
from .app_info_section import AppInfoSection
from .database_section import DatabaseSection
from .folder_section import FolderSection
from .pixiv_section import PixivSection


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

        self.setStyleSheet(
            """
            QLabel#pageTitle {
                font-size: 28px;
                font-weight: 700;
            }

            QLabel#pageDescription {
                font-size: 15px;
                color: #666666;
            }

            QLabel#sectionTitle {
                font-size: 18px;
                font-weight: 700;
            }

            QLabel#fieldLabel {
                font-size: 14px;
                font-weight: 600;
                color: #333333;
            }

            QLabel#statusLabel {
                font-size: 14px;
                color: #198754;
                padding-top: 4px;
            }

            QLabel#infoText {
                font-size: 14px;
                color: #555555;
            }

            QFrame#settingFrame {
                border: 1px solid #dddddd;
                border-radius: 10px;
                background-color: #ffffff;
            }

            QLineEdit {
                border: 1px solid #dddddd;
                border-radius: 6px;
                padding: 8px 10px;
                background-color: #ffffff;
                font-size: 14px;
            }

            QLineEdit:read-only {
                background-color: #f9f9f9;
                color: #555555;
            }

            QPushButton {
                padding: 8px 14px;
                border: 1px solid #cccccc;
                border-radius: 6px;
                background-color: #f5f5f5;
                font-size: 14px;
                font-weight: 600;
                min-width: 100px;
            }

            QPushButton:hover {
                background-color: #eeeeee;
            }

            QPushButton#primaryButton {
                background-color: #198754;
                color: #ffffff;
                border-color: #198754;
            }

            QPushButton#primaryButton:hover {
                background-color: #157347;
            }
            """
        )

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
