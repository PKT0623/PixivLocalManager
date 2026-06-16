from .dashboard_metrics import calculate_dashboard_summary


class DashboardActions:
    def __init__(self, page):
        self.page = page

    def load_dashboard(self):
        artists = self.page.artist_service.get_all_artists()
        self.page.current_artists = artists

        summary = self.calculate_summary(artists)

        self.page.summary_section.update_summary(summary)
        self.page.recent_artists_section.update_recent_artists(artists)
        self.page.recent_scan_section.update_recent_scan_time(artists)
        self.page.recommendation_section.update_recommendations(artists)
        self.page.random_artist_section.update_artists(artists)

    def calculate_summary(self, artists: list[dict]) -> dict:
        return calculate_dashboard_summary(artists)
