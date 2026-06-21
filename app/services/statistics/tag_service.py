import json
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
        tag_display_map = {}

        for item in artist_tag_items:
            for tag in item["tags"]:
                original = tag["original"]
                display = tag["display"]

                tag_counter.update([original])
                tag_display_map[original] = display

        tag_top = [
            {
                "tag": tag_display_map.get(original, original),
                "original_tag": original,
                "display_tag": tag_display_map.get(original, original),
                "count": count,
            }
            for original, count in tag_counter.most_common(limit)
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

    def _parse_tags(self, raw_tags) -> list[dict]:
        if raw_tags is None:
            return []

        if isinstance(raw_tags, list):
            return self._parse_tag_list(raw_tags)

        raw_text = str(raw_tags).strip()

        if raw_text.lower() in self.EMPTY_TAG_VALUES:
            return []

        try:
            parsed = json.loads(raw_text)
        except json.JSONDecodeError:
            return self._parse_legacy_text(raw_text)

        if not isinstance(parsed, list):
            return []

        return self._parse_tag_list(parsed)

    def _parse_tag_list(
        self,
        values: list,
    ) -> list[dict]:
        tags = []

        for value in values:
            if isinstance(value, str):
                tag = value.strip()

                if tag and tag.lower() not in self.EMPTY_TAG_VALUES:
                    tags.append(
                        {
                            "original": tag,
                            "display": tag,
                        }
                    )

                continue

            if not isinstance(value, dict):
                continue

            original = str(
                value.get("original")
                or value.get("name")
                or value.get("tag")
                or ""
            ).strip()
            translated = str(
                value.get("translated")
                or value.get("translated_name")
                or value.get("tag_translation")
                or ""
            ).strip()

            display = translated or original

            if (
                original
                and original.lower() not in self.EMPTY_TAG_VALUES
            ):
                tags.append(
                    {
                        "original": original,
                        "display": display,
                    }
                )

        return tags

    def _parse_legacy_text(
        self,
        raw_text: str,
    ) -> list[dict]:
        tags = []

        for value in raw_text.replace("\n", ",").split(","):
            tag = value.strip()

            if tag and tag.lower() not in self.EMPTY_TAG_VALUES:
                tags.append(
                    {
                        "original": tag,
                        "display": tag,
                    }
                )

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
