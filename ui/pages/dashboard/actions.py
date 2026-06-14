from .utils import count_status, to_int


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
        total_artists = len(artists)
        total_artworks = sum(
            to_int(artist.get("folder_artwork_count", 0))
            for artist in artists
        )

        rating_values = [
            to_int(artist.get("rating", 0), minimum=0, maximum=10)
            for artist in artists
            if to_int(artist.get("rating", 0), minimum=0, maximum=10) > 0
        ]

        average_rating = (
            f"{sum(rating_values) / len(rating_values):.1f}"
            if rating_values
            else "-"
        )

        return {
            "total_artists": total_artists,
            "total_artworks": total_artworks,
            "average_rating": average_rating,
            "unknown_count": count_status(artists, {"unknown"}),
            "latest_count": count_status(artists, {"latest", "up_to_date"}),
            "need_update_count": count_status(artists, {"need_update"}),
        }
