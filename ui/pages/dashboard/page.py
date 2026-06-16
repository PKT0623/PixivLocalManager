from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.services.artist import ArtistService

from .actions import DashboardActions
from .dashboard_styles import DASHBOARD_PAGE_STYLE
from .random_artist_section import RandomArtistSection
from .recent_artists_section import RecentArtistsSection
from .recent_scan_section import RecentScanSection
from .recommendation_section import RecommendationSection
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

        description_label = QLabel(
            "전체 작가 상태와 수집 현황을 요약해서 보여주는 화면입니다."
        )
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

        self.setStyleSheet(DASHBOARD_PAGE_STYLE)

    def load_dashboard(self):
        self.actions.load_dashboard()
