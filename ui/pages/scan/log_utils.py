from datetime import datetime


def build_info_log_row(message: str) -> dict:
    return {
        "time": datetime.now().strftime("%H:%M:%S"),
        "progress": "-",
        "result": "정보",
        "artist_name": message,
        "pixiv_id": "-",
        "artwork_count": "-",
        "file_count": "-",
        "update_status": "-",
    }
