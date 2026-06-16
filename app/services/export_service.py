import csv
from typing import List, Dict, Any

from app.database.artist import ArtistRepository


class ExportService:
    def __init__(self):
        self.repo = ArtistRepository()

    def export_artists_to_csv(
        self,
        file_path: str,
    ) -> str:
        artists: List[Dict[str, Any]] = self.repo.get_all()

        headers = [
            "id",
            "name",
            "pixiv_id",
            "rating",
            "status",
            "folder_path",
            "folder_size_bytes",
            "folder_file_count",
            "folder_artwork_count",
            "local_latest_artwork_ids",
            "pixiv_latest_artwork_ids",
            "update_status",
        ]

        with open(
            file_path,
            "w",
            newline="",
            encoding="utf-8",
        ) as f:
            writer = csv.DictWriter(
                f,
                fieldnames=headers,
            )

            writer.writeheader()

            for artist in artists:
                writer.writerow(
                    {
                        "id": artist.get("id"),
                        "name": artist.get("name"),
                        "pixiv_id": artist.get("pixiv_id"),
                        "rating": artist.get("rating"),
                        "status": artist.get("status"),
                        "folder_path": artist.get("folder_path"),
                        "folder_size_bytes": artist.get(
                            "folder_size_bytes"
                        ),
                        "folder_file_count": artist.get(
                            "folder_file_count"
                        ),
                        "folder_artwork_count": artist.get(
                            "folder_artwork_count"
                        ),
                        "local_latest_artwork_ids": artist.get(
                            "local_latest_artwork_ids"
                        ),
                        "pixiv_latest_artwork_ids": artist.get(
                            "pixiv_latest_artwork_ids"
                        ),
                        "update_status": artist.get(
                            "update_status"
                        ),
                    }
                )

        return file_path
