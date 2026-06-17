from PySide6.QtCore import Signal
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
from .recent_activity_section import RecentActivitySection
from .recommendation_section import RecommendationSection
from .scan_statistics_section import ScanStatisticsSection
from .summary_section import SummarySection
from .top_ranking_section import TopRankingSection
from .update_status_section import UpdateStatusSection


class DashboardPage(QWidget):
    artist_detail_requested = Signal(int)

    def __init__(self):
        super().__init__()

        self.artist_service = ArtistService()
        self.current_artists = []
        self.actions = DashboardActions(self)

        self._setup_ui()
        self._connect_signals()
        self.actions.load_dashboard()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 24)
        layout.setSpacing(14)

        header_layout = QHBoxLayout()

        title_label = QLabel("대시보드")
        title_label.setObjectName("pageTitle")

        self.refresh_button = QPushButton("새로고침")
        self.refresh_button.setObjectName("refreshButton")
        self.refresh_button.clicked.connect(self.actions.load_dashboard)

        header_layout.addWidget(title_label, 1)
        header_layout.addWidget(self.refresh_button)

        self.summary_section = SummarySection()
        self.update_status_section = UpdateStatusSection()
        self.scan_statistics_section = ScanStatisticsSection()
        self.recent_activity_section = RecentActivitySection()
        self.top_ranking_section = TopRankingSection()
        self.recommendation_section = RecommendationSection()
        self.random_artist_section = RandomArtistSection()

        upper_layout = QHBoxLayout()
        upper_layout.setSpacing(14)

        left_layout = QVBoxLayout()
        left_layout.setSpacing(14)

        right_layout = QVBoxLayout()
        right_layout.setSpacing(14)

        left_layout.addLayout(self.summary_section, 1)
        left_layout.addWidget(self.recent_activity_section, 4)

        top_right_layout = QHBoxLayout()
        top_right_layout.setSpacing(14)

        top_right_layout.addWidget(self.update_status_section, 1)
        top_right_layout.addWidget(self.scan_statistics_section, 1)

        right_layout.addLayout(top_right_layout, 1)
        right_layout.addWidget(self.top_ranking_section, 4)

        upper_layout.addLayout(left_layout, 5)
        upper_layout.addLayout(right_layout, 5)

        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(14)

        bottom_layout.addWidget(self.recommendation_section, 3)
        bottom_layout.addWidget(self.random_artist_section, 1)

        layout.addLayout(header_layout)
        layout.addLayout(upper_layout, 6)
        layout.addLayout(bottom_layout, 4)

        self.setStyleSheet(DASHBOARD_PAGE_STYLE)

    def _connect_signals(self):
        self.recent_activity_section.artist_detail_requested.connect(
            self.artist_detail_requested.emit
        )
        self.top_ranking_section.artist_detail_requested.connect(
            self.artist_detail_requested.emit
        )

    def load_dashboard(self):
        self.actions.load_dashboard()
