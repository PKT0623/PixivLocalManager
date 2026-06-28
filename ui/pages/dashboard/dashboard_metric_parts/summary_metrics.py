from ..utils import count_status, format_bytes
from .artwork_metrics import (
    calculate_favorite_artists,
    calculate_recent_scan_time,
    calculate_total_artworks,
    calculate_total_files,
    calculate_total_folder_size,
)


def calculate_dashboard_summary(
    artists: list[dict],
    update_status_summary: dict,
    follow_user_count: int = 0,
    bookmark_artwork_count: int = 0,
) -> dict:
    total_artists = len(artists)
    total_artworks = calculate_total_artworks(artists)
    total_files = calculate_total_files(artists)
    total_folder_size = calculate_total_folder_size(artists)

    return {
        "total_artists": total_artists,
        "favorite_artists": calculate_favorite_artists(artists),
        "follow_users": follow_user_count,
        "bookmark_artworks": bookmark_artwork_count,
        "need_update_count": count_status(artists, {"need_update"}),
        "error_count": count_status(artists, {"error"}),
        "recent_scan": calculate_recent_scan_time(artists),
        "total_artworks": total_artworks,
        "total_files": total_files,
        "total_folder_size": format_bytes(total_folder_size),
        "update_status_summary": update_status_summary,
    }
