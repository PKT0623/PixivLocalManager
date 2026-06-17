def to_int(value, minimum: int = 0, maximum: int = 10) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError):
        number = minimum

    return max(minimum, min(maximum, number))


class StatisticsFavoriteService:
    def get_favorite_statistics(self, artists: list[dict]) -> dict:
        total_count = len(artists)
        favorite_artists = self._get_favorite_artists(artists)
        favorite_count = len(favorite_artists)

        return {
            "favorite_count": favorite_count,
            "favorite_ratio": self._calculate_ratio(
                count=favorite_count,
                total_count=total_count,
            ),
            "favorite_average_rating": self._calculate_average_rating(
                favorite_artists
            ),
        }

    def _get_favorite_artists(self, artists: list[dict]) -> list[dict]:
        return [
            artist
            for artist in artists
            if bool(artist.get("is_favorite", 0))
        ]

    def _calculate_average_rating(self, artists: list[dict]) -> float:
        ratings = [
            to_int(artist.get("rating", 0))
            for artist in artists
            if to_int(artist.get("rating", 0)) > 0
        ]

        if not ratings:
            return 0.0

        return round(
            sum(ratings) / len(ratings),
            1,
        )

    def _calculate_ratio(
        self,
        count: int,
        total_count: int,
    ) -> float:
        if total_count <= 0:
            return 0.0

        return round(
            count / total_count * 100,
            1,
        )
