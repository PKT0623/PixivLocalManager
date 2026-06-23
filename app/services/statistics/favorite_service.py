def to_int(value, minimum: int = 0, maximum: int = 10) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError):
        number = minimum

    return max(minimum, min(maximum, number))


class StatisticsFavoriteService:
    def get_favorite_statistics(self, artists: list[dict]) -> dict:
        total_count = len(artists)
        favorite_count = 0
        favorite_rating_sum = 0
        favorite_rating_count = 0

        for artist in artists:
            if not bool(artist.get("is_favorite", 0)):
                continue

            favorite_count += 1

            rating = to_int(artist.get("rating", 0))

            if rating <= 0:
                continue

            favorite_rating_sum += rating
            favorite_rating_count += 1

        return {
            "favorite_count": favorite_count,
            "favorite_ratio": self._calculate_ratio(
                count=favorite_count,
                total_count=total_count,
            ),
            "favorite_average_rating": self._calculate_average(
                total_value=favorite_rating_sum,
                total_count=favorite_rating_count,
            ),
        }

    def _calculate_average(
        self,
        total_value: int,
        total_count: int,
    ) -> float:
        if total_count <= 0:
            return 0.0

        return round(
            total_value / total_count,
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
