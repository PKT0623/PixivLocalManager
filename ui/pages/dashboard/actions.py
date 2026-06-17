from app.database import ArtistUpdateHistoryRepository

from .dashboard_metrics import (
    build_recent_activity_data,
    build_scan_statistics_data,
    build_top_ranking_data,
    calculate_dashboard_summary,
    calculate_update_status_summary,
)


class DashboardActions:
    RECENT_ACTIVITY_LIMIT = 50

    def __init__(self, page):
        self.page = page
        self.history_repo = ArtistUpdateHistoryRepository()

    def load_dashboard(self):
        artists = self.page.artist_service.get_all_artists()
        recent_histories = self.history_repo.get_recent(
            limit=self.RECENT_ACTIVITY_LIMIT,
        )
        today_histories = self.history_repo.get_today_histories()
        latest_histories = self.history_repo.get_latest_history_per_artist()
        recent_error_histories = self.history_repo.get_recent_error_histories(
            limit=self.RECENT_ACTIVITY_LIMIT,
        )
        missing_increased_histories = (
            self.history_repo.get_recent_missing_increased_artists(
                limit=self.RECENT_ACTIVITY_LIMIT,
            )
        )

        self.page.current_artists = artists

        update_status_summary = calculate_update_status_summary(
            artists=artists,
            today_histories=today_histories,
            latest_histories=latest_histories,
            history_repo=self.history_repo,
        )
        summary = self.calculate_summary(
            artists=artists,
            update_status_summary=update_status_summary,
        )
        recent_activity_data = build_recent_activity_data(
            artists=artists,
            recent_histories=recent_histories,
            recent_error_histories=recent_error_histories,
            missing_increased_histories=missing_increased_histories,
            limit=self.RECENT_ACTIVITY_LIMIT,
        )
        scan_statistics_data = build_scan_statistics_data(
            recent_histories=recent_histories,
        )
        top_ranking_data = build_top_ranking_data(
            artists=artists,
        )

        self.page.summary_section.update_summary(summary)
        self.page.update_status_section.update_status_summary(
            update_status_summary
        )
        self.page.recent_activity_section.update_recent_activity(
            recent_activity_data
        )
        self.page.scan_statistics_section.update_scan_statistics(
            scan_statistics_data
        )
        self.page.top_ranking_section.update_top_rankings(top_ranking_data)
        self.page.recommendation_section.update_recommendations(artists)
        self.page.random_artist_section.update_artists(artists)

    def calculate_summary(
        self,
        artists: list[dict],
        update_status_summary: dict,
    ) -> dict:
        return calculate_dashboard_summary(
            artists=artists,
            update_status_summary=update_status_summary,
        )
