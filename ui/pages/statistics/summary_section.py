from PySide6.QtWidgets import QGridLayout

from .formatters import (
    format_bytes,
    format_count,
    format_number,
    format_rating,
)
from .summary_card import StatisticsSummaryCard


class StatisticsSummarySection(QGridLayout):
    def __init__(self):
        super().__init__()

        self.setSpacing(8)

        self.cards = {
            "total_artists": StatisticsSummaryCard("전체 작가 수"),
            "total_artworks": StatisticsSummaryCard("전체 작품 수"),
            "total_files": StatisticsSummaryCard("전체 파일 수"),
            "total_folder_size": StatisticsSummaryCard("총 저장 용량"),
            "favorite_count": StatisticsSummaryCard("즐겨찾기 작가 수"),
            "follow_count": StatisticsSummaryCard("팔로우 수"),
            "bookmark_count": StatisticsSummaryCard("북마크 수"),
            "average_rating": StatisticsSummaryCard("평균 평점"),
            "average_artworks": StatisticsSummaryCard("평균 작품 수"),
            "average_files": StatisticsSummaryCard("평균 파일 수"),
            "average_folder_size": StatisticsSummaryCard("평균 저장 용량"),
            "favorite_average_rating": StatisticsSummaryCard(
                "즐겨찾기 평균 평점"
            ),
        }

        self._setup_ui()

    def _setup_ui(self):
        self.addWidget(self.cards["total_artists"], 0, 0)
        self.addWidget(self.cards["total_artworks"], 0, 1)
        self.addWidget(self.cards["total_files"], 0, 2)
        self.addWidget(self.cards["total_folder_size"], 0, 3)
        self.addWidget(self.cards["favorite_count"], 0, 4)
        self.addWidget(self.cards["favorite_average_rating"], 0, 5)

        self.addWidget(self.cards["average_rating"], 1, 0)
        self.addWidget(self.cards["average_artworks"], 1, 1)
        self.addWidget(self.cards["average_files"], 1, 2)
        self.addWidget(self.cards["average_folder_size"], 1, 3)
        self.addWidget(self.cards["follow_count"], 1, 4)
        self.addWidget(self.cards["bookmark_count"], 1, 5)

    def update_summary(
        self,
        summary: dict,
        favorite: dict | None = None,
        pixiv_management: dict | None = None,
    ):
        favorite = favorite or {}
        pixiv_management = pixiv_management or {}

        self.cards["total_artists"].set_value(
            format_count(summary.get("total_artists", 0))
        )
        self.cards["total_artworks"].set_value(
            format_count(summary.get("total_artworks", 0))
        )
        self.cards["total_files"].set_value(
            format_count(summary.get("total_files", 0))
        )
        self.cards["total_folder_size"].set_value(
            format_bytes(summary.get("total_folder_size", 0))
        )
        self.cards["favorite_count"].set_value(
            format_count(favorite.get("favorite_count", 0))
        )
        self.cards["follow_count"].set_value(
            format_count(pixiv_management.get("follow_count", 0))
        )
        self.cards["average_rating"].set_value(
            format_rating(summary.get("average_rating", 0))
        )
        self.cards["average_artworks"].set_value(
            format_number(summary.get("average_artworks", 0))
        )
        self.cards["average_files"].set_value(
            format_number(summary.get("average_files", 0))
        )
        self.cards["average_folder_size"].set_value(
            format_bytes(summary.get("average_folder_size", 0))
        )
        self.cards["favorite_average_rating"].set_value(
            format_rating(
                favorite.get("favorite_average_rating", 0)
            )
        )
        self.cards["bookmark_count"].set_value(
            format_count(pixiv_management.get("bookmark_count", 0))
        )
