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

        unrated_count = self._count_empty_field(
            artists=artists,
            field_name="rating",
            empty_checker=self._is_empty_rating,
        )
        untagged_count = self._count_empty_field(
            artists=artists,
            field_name="artist_tags",
            empty_checker=self._is_empty_text,
        )
        memo_empty_count = self._count_empty_field(
            artists=artists,
            field_name="memo",
            empty_checker=self._is_empty_text,
        )

        return {
            "total_count": total_count,
            "rating_input_count": total_count - unrated_count,
            "tag_input_count": total_count - untagged_count,
            "memo_input_count": total_count - memo_empty_count,
            "unrated_count": unrated_count,
            "untagged_count": untagged_count,
            "memo_empty_count": memo_empty_count,
            "rating_input_ratio": self._calculate_ratio(
                total_count - unrated_count,
                total_count,
            ),
            "tag_input_ratio": self._calculate_ratio(
                total_count - untagged_count,
                total_count,
            ),
            "memo_input_ratio": self._calculate_ratio(
                total_count - memo_empty_count,
                total_count,
            ),
        }

    def _count_empty_field(
        self,
        artists: list[dict],
        field_name: str,
        empty_checker,
    ) -> int:
        return sum(
            1
            for artist in artists
            if empty_checker(artist.get(field_name))
        )

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
