from PySide6.QtWidgets import (
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
from .progress_section import ScanProgressSection


class ScanPage(QWidget):
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
            "Pixiv 이미지 폴더를 선택하고 최대 3단계 하위 폴더까지 분석해 DB에 등록합니다."
        )
        description_label.setObjectName("pageDescription")

        self.folder_section = ScanFolderSection()
        self.progress_section = ScanProgressSection()
        self.folder_section.layout().addWidget(self.progress_section)

        log_header_layout = QHBoxLayout()

        log_label = QLabel("결과 로그")
        log_label.setObjectName("sectionTitle")

        self.clear_log_button = QPushButton("로그 지우기")
        self.clear_log_button.setObjectName("clearLogButton")

        log_header_layout.addWidget(log_label)
        log_header_layout.addStretch()
        log_header_layout.addWidget(self.clear_log_button)

        self.log_table = ScanLogTable()

        layout.addWidget(title_label)
        layout.addWidget(description_label)
        layout.addWidget(self.folder_section)
        layout.addLayout(log_header_layout)
        layout.addWidget(self.log_table, 1)

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

            QLabel#subText {
                font-size: 14px;
                color: #555555;
            }

            QFrame#inputFrame {
                border: 1px solid #dddddd;
                border-radius: 10px;
                background-color: #ffffff;
            }

            QLineEdit {
                border: 1px solid #dddddd;
                border-radius: 6px;
                padding: 8px 10px;
                background-color: #f9f9f9;
                font-size: 14px;
            }

            QPushButton {
                padding: 8px 14px;
                border: 1px solid #cccccc;
                border-radius: 6px;
                background-color: #f5f5f5;
                font-size: 14px;
                font-weight: 600;
            }

            QPushButton:hover {
                background-color: #eeeeee;
            }

            QPushButton#scanButton {
                background-color: #198754;
                color: #ffffff;
                border-color: #198754;
                min-width: 110px;
            }

            QPushButton#scanButton:hover {
                background-color: #157347;
            }

            QPushButton#folderSelectButton,
            QPushButton#clearLogButton {
                min-width: 100px;
            }

            QProgressBar {
                border: 1px solid #cccccc;
                border-radius: 8px;
                text-align: center;
                height: 22px;
                background-color: #f5f5f5;
                font-size: 13px;
                font-weight: 600;
            }

            QProgressBar::chunk {
                border-radius: 8px;
                background-color: #198754;
            }

            QTableWidget {
                border: 1px solid #dddddd;
                border-radius: 10px;
                background-color: #ffffff;
                gridline-color: #eeeeee;
                font-size: 13px;
            }

            QHeaderView::section {
                background-color: #f5f5f5;
                border: none;
                border-bottom: 1px solid #dddddd;
                padding: 8px;
                font-weight: 700;
            }

            QTableWidget::item {
                padding: 4px;
            }
            """
        )

    def _connect_signals(self):
        self.folder_section.folder_select_button.clicked.connect(
            self.actions.select_folder
        )
        self.folder_section.scan_button.clicked.connect(
            self.actions.start_scan
        )
        self.clear_log_button.clicked.connect(
            self.log_table.clear_log
        )
