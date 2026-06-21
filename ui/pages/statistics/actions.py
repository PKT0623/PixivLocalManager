from app.services import StatisticsService


class StatisticsActions:
    def __init__(self, page):
        self.page = page
        self.statistics_service = StatisticsService()

    def load_statistics(self):
        statistics = self.statistics_service.get_statistics()

        self.page.current_statistics = statistics
        self.page.summary_section.update_summary(
            summary=statistics.get("summary", {}),
            favorite=statistics.get("favorite", {}),
            pixiv_management=statistics.get("pixiv_management", {}),
        )
        self.page.status_section.update_status(
            statistics.get("status", {})
        )
        self.page.rating_section.update_rating(
            statistics.get("rating", {})
        )
        self.page.ranking_section.update_ranking(
            statistics.get("ranking", {})
        )
        self.page.tag_section.update_tag(
            statistics.get("tag", {})
        )
        self.page.quality_section.update_quality(
            statistics.get("quality", {})
        )
        self.page.trend_section.update_trend(
            statistics.get("trend", {})
        )
