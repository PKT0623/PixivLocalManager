from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.services.artist_service import ArtistService

from .actions import DashboardActions
from .recent_artists_section import RecentArtistsSection
from .recent_scan_section import RecentScanSection
from .recommendation_section import RecommendationSection
from .random_artist_section import RandomArtistSection
from .summary_section import SummarySection


class DashboardPage(QWidget):
    def __init__(self):
        super().__init__()

        self.artist_service = ArtistService()
        self.current_artists = []
        self.actions = DashboardActions(self)

        self._setup_ui()
        self.actions.load_dashboard()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(20)

        header_layout = QHBoxLayout()

        title_box = QVBoxLayout()
        title_box.setSpacing(4)

        title_label = QLabel("대시보드")
        title_label.setObjectName("pageTitle")

        description_label = QLabel("전체 작가 상태와 수집 현황을 요약해서 보여주는 화면입니다.")
        description_label.setObjectName("pageDescription")

        title_box.addWidget(title_label)
        title_box.addWidget(description_label)

        self.refresh_button = QPushButton("새로고침")
        self.refresh_button.setObjectName("refreshButton")
        self.refresh_button.clicked.connect(self.actions.load_dashboard)

        header_layout.addLayout(title_box, 1)
        header_layout.addWidget(self.refresh_button)

        self.summary_section = SummarySection()
        self.recent_artists_section = RecentArtistsSection()
        self.recent_scan_section = RecentScanSection()
        self.recommendation_section = RecommendationSection()
        self.random_artist_section = RandomArtistSection()

        detail_layout = QHBoxLayout()
        detail_layout.setSpacing(16)

        left_layout = QVBoxLayout()
        left_layout.setSpacing(16)

        right_layout = QVBoxLayout()
        right_layout.setSpacing(16)

        left_layout.addWidget(self.recent_artists_section, 1)
        left_layout.addWidget(self.recommendation_section, 1)

        right_layout.addWidget(self.recent_scan_section)
        right_layout.addWidget(self.random_artist_section, 1)

        detail_layout.addLayout(left_layout, 2)
        detail_layout.addLayout(right_layout, 1)

        layout.addLayout(header_layout)
        layout.addLayout(self.summary_section)
        layout.addLayout(detail_layout, 1)

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

            QPushButton {
                padding: 7px 12px;
                border: 1px solid #cccccc;
                border-radius: 6px;
                background-color: #f5f5f5;
                font-size: 13px;
                font-weight: 600;
            }

            QPushButton:hover {
                background-color: #eeeeee;
            }

            QPushButton#refreshButton,
            QPushButton#limitButton {
                min-width: 58px;
            }

            QPushButton#limitButton[active="true"] {
                background-color: #198754;
                color: #ffffff;
                border-color: #198754;
            }

            QFrame#summaryCard,
            QFrame#detailCard,
            QFrame#artistCard,
            QFrame#randomCard {
                border: 1px solid #dddddd;
                border-radius: 10px;
                background-color: #ffffff;
            }

            QLabel#cardTitle {
                font-size: 14px;
                color: #666666;
                font-weight: 600;
            }

            QLabel#cardValue {
                font-size: 30px;
                font-weight: 800;
                color: #202124;
            }

            QLabel#sectionTitle {
                font-size: 18px;
                font-weight: 700;
            }

            QLabel#subText {
                font-size: 13px;
                color: #777777;
            }

            QLabel#recentScanValue {
                font-size: 18px;
                font-weight: 700;
                color: #202124;
            }

            QLabel#thumbnailLabel {
                background-color: #f1f3f5;
                border: 1px solid #dddddd;
                border-radius: 8px;
                color: #777777;
            }

            QLabel#artistName {
                font-size: 15px;
                font-weight: 700;
            }

            QLabel#artistInfo {
                font-size: 13px;
                color: #555555;
            }

            QLabel#randomHiddenText {
                font-size: 18px;
                font-weight: 800;
                color: #202124;
            }

            QScrollArea {
                border: none;
                background-color: transparent;
            }

            QTableWidget {
                border: none;
                background-color: #ffffff;
                gridline-color: #eeeeee;
                font-size: 14px;
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

    def load_dashboard(self):
        self.actions.load_dashboard()
