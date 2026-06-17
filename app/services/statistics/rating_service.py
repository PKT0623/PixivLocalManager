def to_int(value, minimum: int = 0, maximum: int = 10) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError):
        number = minimum

    return max(minimum, min(maximum, number))


class StatisticsRatingService:
    RATING_MIN = 0
    RATING_MAX = 10

    def get_rating_statistics(self, artists: list[dict]) -> dict:
        ratings = self._get_ratings(artists)
        rated_ratings = [
            rating
            for rating in ratings
            if rating > 0
        ]

        return {
            "average_rating": self.calculate_average_rating(rated_ratings),
            "rating_distribution": self.calculate_rating_distribution(
                ratings
            ),
            "rated_count": len(rated_ratings),
            "unrated_count": len(artists) - len(rated_ratings),
        }

    def calculate_average_rating(self, ratings: list[int]) -> float:
        if not ratings:
            return 0.0

        return round(
            sum(ratings) / len(ratings),
            1,
        )

    def calculate_rating_distribution(
        self,
        ratings: list[int],
    ) -> dict[int, int]:
        distribution = {
            rating: 0
            for rating in range(self.RATING_MIN, self.RATING_MAX + 1)
        }

        for rating in ratings:
            distribution[rating] += 1

        return distribution

    def _get_ratings(self, artists: list[dict]) -> list[int]:
        return [
            to_int(artist.get("rating", 0))
            for artist in artists
        ]
