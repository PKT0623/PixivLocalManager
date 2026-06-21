from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from .actions import StatisticsActions
from .quality_section import StatisticsQualitySection
from .ranking_section import StatisticsRankingSection
from .rating_section import StatisticsRatingSection
from .status_section import StatisticsStatusSection
from .styles import STATISTICS_PAGE_STYLE
from .summary_section import StatisticsSummarySection
from .trend_section import StatisticsTrendSection
from .tag_section import StatisticsTagSection


class StatisticsPage(QWidget):
    def __init__(self):
        super().__init__()

        self.current_statistics = {}
        self.actions = StatisticsActions(self)

        self._setup_ui()
        self.actions.load_statistics()

    def _setup_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(32, 28, 32, 24)
        root_layout.setSpacing(16)

        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)

        title_label = QLabel("통계 분석")
        title_label.setObjectName("pageTitle")

        self.refresh_button = QPushButton("새로고침")
        self.refresh_button.setObjectName("refreshButton")
        self.refresh_button.clicked.connect(self.actions.load_statistics)

        header_layout.addWidget(title_label, 1)
        header_layout.addWidget(self.refresh_button)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)

        content_widget = QWidget()
        content_widget.setObjectName("statisticsContent")

        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(14)

        self.summary_section = StatisticsSummarySection()
        self.quality_section = StatisticsQualitySection()
        self.ranking_section = StatisticsRankingSection()
        self.status_section = StatisticsStatusSection()
        self.tag_section = StatisticsTagSection()
        self.rating_section = StatisticsRatingSection()
        self.trend_section = StatisticsTrendSection()

        self.quality_section.setMinimumHeight(230)
        self.quality_section.setMaximumHeight(280)

        self.status_section.setMinimumHeight(220)
        self.status_section.setMaximumHeight(270)

        self.rating_section.setMinimumHeight(300)
        self.rating_section.setMaximumHeight(350)

        self.ranking_section.setMinimumHeight(520)
        self.tag_section.setMinimumHeight(520)
        self.trend_section.setMinimumHeight(220)

        main_layout = QHBoxLayout()
        main_layout.setSpacing(14)

        left_column = QVBoxLayout()
        left_column.setSpacing(14)

        summary_layout = QHBoxLayout()
        summary_layout.setSpacing(0)
        summary_layout.addLayout(self.summary_section)

        ranking_tag_layout = QHBoxLayout()
        ranking_tag_layout.setSpacing(14)
        ranking_tag_layout.addWidget(self.ranking_section, 1)
        ranking_tag_layout.addWidget(self.tag_section, 1)

        left_column.addLayout(summary_layout)
        left_column.addLayout(ranking_tag_layout, 1)

        right_column = QVBoxLayout()
        right_column.setSpacing(14)
        right_column.addWidget(self.quality_section)
        right_column.addWidget(self.status_section)
        right_column.addWidget(self.rating_section)
        right_column.addWidget(self.trend_section, 1)

        main_layout.addLayout(left_column, 2)
        main_layout.addLayout(right_column, 1)

        content_layout.addLayout(main_layout)

        scroll_area.setWidget(content_widget)

        root_layout.addLayout(header_layout)
        root_layout.addWidget(scroll_area, 1)

        self.setStyleSheet(STATISTICS_PAGE_STYLE)

    def load_statistics(self):
        self.actions.load_statistics()
