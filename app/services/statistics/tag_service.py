from collections import Counter


class StatisticsTagService:
    DEFAULT_LIMIT = 20
    EMPTY_TAG_VALUES = {
        "",
        "[]",
        "{}",
        "null",
        "none",
    }

    def get_tag_statistics(
        self,
        artists: list[dict],
        limit: int = DEFAULT_LIMIT,
    ) -> dict:
        artist_tag_items = self._build_artist_tag_items(artists)
        tag_counter = Counter()

        for item in artist_tag_items:
            tag_counter.update(item["tags"])

        tag_top = [
            {
                "tag": tag,
                "count": count,
            }
            for tag, count in tag_counter.most_common(limit)
        ]

        tag_artist_top = sorted(
            [
                {
                    "artist": item["artist"],
                    "tag_count": len(item["tags"]),
                }
                for item in artist_tag_items
                if item["tags"]
            ],
            key=lambda item: (
                item["tag_count"],
                str(item["artist"].get("artist_name", "") or ""),
            ),
            reverse=True,
        )[:limit]

        return {
            "total_tag_count": len(tag_counter),
            "tagged_artist_count": self._count_tagged_artists(
                artist_tag_items
            ),
            "untagged_artist_count": self._count_untagged_artists(
                artist_tag_items
            ),
            "tag_top": tag_top,
            "tag_artist_top": tag_artist_top,
        }

    def _build_artist_tag_items(
        self,
        artists: list[dict],
    ) -> list[dict]:
        return [
            {
                "artist": artist,
                "tags": self._parse_tags(
                    artist.get("artist_tags", "")
                ),
            }
            for artist in artists
        ]

    def _parse_tags(self, raw_tags) -> list[str]:
        if raw_tags is None:
            return []

        raw_text = str(raw_tags).strip()

        if raw_text.lower() in self.EMPTY_TAG_VALUES:
            return []

        if isinstance(raw_tags, list):
            values = raw_tags
        else:
            values = raw_text.replace("\n", ",").split(",")

        tags = []

        for value in values:
            tag = str(value).strip()

            if tag.lower() in self.EMPTY_TAG_VALUES:
                continue

            tags.append(tag)

        return tags

    def _count_tagged_artists(
        self,
        artist_tag_items: list[dict],
    ) -> int:
        return sum(
            1
            for item in artist_tag_items
            if item["tags"]
        )

    def _count_untagged_artists(
        self,
        artist_tag_items: list[dict],
    ) -> int:
        return sum(
            1
            for item in artist_tag_items
            if not item["tags"]
        )
