from .utils import count_status, to_int


def calculate_dashboard_summary(artists: list[dict]) -> dict:
    rating_values = [
        to_int(artist.get("rating", 0), minimum=0, maximum=10)
        for artist in artists
        if to_int(artist.get("rating", 0), minimum=0, maximum=10) > 0
    ]

    return {
        "total_artists": len(artists),
        "total_artworks": calculate_total_artworks(artists),
        "average_rating": calculate_average_rating(rating_values),
        "unknown_count": count_status(artists, {"unknown"}),
        "latest_count": count_status(artists, {"latest", "up_to_date"}),
        "need_update_count": count_status(artists, {"need_update"}),
    }


def calculate_total_artworks(artists: list[dict]) -> int:
    return sum(
        to_int(artist.get("folder_artwork_count", 0))
        for artist in artists
    )


def calculate_average_rating(rating_values: list[int]) -> str:
    if not rating_values:
        return "-"

    return f"{sum(rating_values) / len(rating_values):.1f}"
