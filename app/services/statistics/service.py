from app.database import ArtistRepository

from .favorite_service import StatisticsFavoriteService
from .pixiv_management_service import StatisticsPixivManagementService
from .quality_service import StatisticsQualityService
from .ranking_service import StatisticsRankingService, to_int
from .rating_service import StatisticsRatingService
from .status_service import StatisticsStatusService
from .tag_service import StatisticsTagService
from .trend_service import StatisticsTrendService


class StatisticsService:
    DEFAULT_RANKING_LIMIT = 50

    def __init__(self):
        self.artist_repo = ArtistRepository()
        self.ranking_service = StatisticsRankingService()
        self.rating_service = StatisticsRatingService()
        self.status_service = StatisticsStatusService()
        self.tag_service = StatisticsTagService()
        self.favorite_service = StatisticsFavoriteService()
        self.quality_service = StatisticsQualityService()
        self.pixiv_management_service = StatisticsPixivManagementService()
        self.trend_service = StatisticsTrendService()

    def get_statistics(
        self,
        ranking_limit: int = DEFAULT_RANKING_LIMIT,
    ) -> dict:
        artists = self.artist_repo.get_all()

        rating_statistics = self.rating_service.get_rating_statistics(
            artists
        )

        return {
            "summary": self.get_summary_statistics(
                artists=artists,
                average_rating=rating_statistics["average_rating"],
            ),
            "status": self.status_service.get_status_statistics(artists),
            "rating": rating_statistics,
            "ranking": self.ranking_service.get_ranking_statistics(
                artists=artists,
                limit=ranking_limit,
            ),
            "tag": self.tag_service.get_tag_statistics(
                artists=artists,
                limit=ranking_limit,
            ),
            "favorite": self.favorite_service.get_favorite_statistics(
                artists
            ),
            "quality": self.quality_service.get_quality_statistics(
                artists
            ),
            "pixiv_management": (
                self.pixiv_management_service
                .get_pixiv_management_statistics()
            ),
            "trend": self.trend_service.get_trend_statistics(),
        }

    def get_summary_statistics(
        self,
        artists: list[dict],
        average_rating: float,
    ) -> dict:
        total_artists = len(artists)
        total_artworks = self.calculate_total(
            artists=artists,
            field_name="folder_artwork_count",
        )
        total_files = self.calculate_total(
            artists=artists,
            field_name="folder_file_count",
        )
        total_folder_size = self.calculate_total(
            artists=artists,
            field_name="folder_size_bytes",
            maximum=10**18,
        )

        return {
            "total_artists": total_artists,
            "total_artworks": total_artworks,
            "total_files": total_files,
            "total_folder_size": total_folder_size,
            "average_rating": average_rating,
            "average_artworks": self.calculate_average(
                total_value=total_artworks,
                total_count=total_artists,
            ),
            "average_files": self.calculate_average(
                total_value=total_files,
                total_count=total_artists,
            ),
            "average_folder_size": self.calculate_average(
                total_value=total_folder_size,
                total_count=total_artists,
            ),
        }

    def calculate_total(
        self,
        artists: list[dict],
        field_name: str,
        maximum: int = 999999,
    ) -> int:
        return sum(
            to_int(
                artist.get(field_name, 0),
                maximum=maximum,
            )
            for artist in artists
        )

    def calculate_average(
        self,
        total_value: int,
        total_count: int,
    ) -> float:
        if total_count <= 0:
            return 0.0

        return round(
            total_value / total_count,
            1,
        )
