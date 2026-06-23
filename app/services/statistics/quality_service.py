class StatisticsQualityService:
    EMPTY_TEXT_VALUES = {
        "",
        "[]",
        "{}",
        "null",
        "none",
    }

    def get_quality_statistics(self, artists: list[dict]) -> dict:
        total_count = len(artists)
        unrated_count = 0
        untagged_count = 0
        memo_empty_count = 0

        for artist in artists:
            if self._is_empty_rating(artist.get("rating")):
                unrated_count += 1

            if self._is_empty_text(artist.get("artist_tags")):
                untagged_count += 1

            if self._is_empty_text(artist.get("memo")):
                memo_empty_count += 1

        rating_input_count = total_count - unrated_count
        tag_input_count = total_count - untagged_count
        memo_input_count = total_count - memo_empty_count

        return {
            "total_count": total_count,
            "rating_input_count": rating_input_count,
            "tag_input_count": tag_input_count,
            "memo_input_count": memo_input_count,
            "unrated_count": unrated_count,
            "untagged_count": untagged_count,
            "memo_empty_count": memo_empty_count,
            "rating_input_ratio": self._calculate_ratio(
                rating_input_count,
                total_count,
            ),
            "tag_input_ratio": self._calculate_ratio(
                tag_input_count,
                total_count,
            ),
            "memo_input_ratio": self._calculate_ratio(
                memo_input_count,
                total_count,
            ),
        }

    def _is_empty_rating(self, value) -> bool:
        try:
            return int(value) <= 0
        except (TypeError, ValueError):
            return True

    def _is_empty_text(self, value) -> bool:
        if value is None:
            return True

        return str(value).strip().lower() in self.EMPTY_TEXT_VALUES

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
