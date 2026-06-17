def to_int(value, minimum: int = 0, maximum: int = 10**18) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError):
        number = minimum

    return max(minimum, min(maximum, number))


class StatisticsRankingService:
    DEFAULT_LIMIT = 20

    def get_ranking_statistics(
        self,
        artists: list[dict],
        limit: int = DEFAULT_LIMIT,
    ) -> dict:
        return {
            "top_artworks": self.get_top_artists_by_field(
                artists=artists,
                field_name="folder_artwork_count",
                limit=limit,
            ),
            "top_files": self.get_top_artists_by_field(
                artists=artists,
                field_name="folder_file_count",
                limit=limit,
            ),
            "top_storage": self.get_top_artists_by_field(
                artists=artists,
                field_name="folder_size_bytes",
                limit=limit,
            ),
            "top_rating": self.get_top_rating_artists(
                artists=artists,
                limit=limit,
            ),
        }

    def get_top_artists_by_field(
        self,
        artists: list[dict],
        field_name: str,
        limit: int = DEFAULT_LIMIT,
    ) -> list[dict]:
        valid_artists = [
            artist
            for artist in artists
            if to_int(artist.get(field_name, 0)) > 0
        ]

        return sorted(
            valid_artists,
            key=lambda artist: to_int(artist.get(field_name, 0)),
            reverse=True,
        )[:limit]

    def get_top_rating_artists(
        self,
        artists: list[dict],
        limit: int = DEFAULT_LIMIT,
    ) -> list[dict]:
        valid_artists = [
            artist
            for artist in artists
            if to_int(artist.get("rating", 0), maximum=10) > 0
        ]

        return sorted(
            valid_artists,
            key=lambda artist: (
                to_int(artist.get("rating", 0), maximum=10),
                to_int(artist.get("folder_artwork_count", 0)),
                str(artist.get("artist_name", "") or ""),
            ),
            reverse=True,
        )[:limit]
