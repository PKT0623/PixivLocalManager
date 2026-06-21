class PixivMetadataTagParser:
    def extract_user_tags(
        self,
        body: dict,
    ) -> list[dict]:
        tags = []

        for key in (
            "tags",
            "tag",
            "popularTags",
            "workspaceTags",
        ):
            value = body.get(key)

            if isinstance(value, list):
                tags.extend(self.normalize_tag_list(value))
            elif isinstance(value, dict):
                tags.extend(self.normalize_tag_dict(value))

        return self.deduplicate_tags(tags)

    def extract_artwork_tags(
        self,
        body: dict,
    ) -> list[dict]:
        tag_container = body.get("tags", {})
        raw_tags = []

        if isinstance(tag_container, dict):
            raw_tags = tag_container.get("tags", [])

        if not isinstance(raw_tags, list):
            raw_tags = []

        tags = []

        for item in raw_tags:
            if not isinstance(item, dict):
                continue

            original = str(item.get("tag", "") or "").strip()

            if not original:
                continue

            tags.append(
                {
                    "original": original,
                    "translated": self.extract_translated_tag(item),
                    "artwork_count": 0,
                    "custom_translation": False,
                }
            )

        return self.deduplicate_tags(tags)

    def extract_user_illust_tag_statistics(
        self,
        body,
    ) -> list[dict]:
        if not isinstance(body, list):
            return []

        tags = []

        for item in body:
            if not isinstance(item, dict):
                continue

            original = str(item.get("tag", "") or "").strip()

            if not original:
                continue

            translated = str(
                item.get("tag_translation", "")
                or item.get("translated", "")
                or item.get("translated_name", "")
                or ""
            ).strip()

            count = self.to_non_negative_int(
                item.get("cnt")
                or item.get("count")
                or item.get("artwork_count")
                or 0
            )

            tags.append(
                {
                    "original": original,
                    "translated": translated,
                    "artwork_count": count,
                    "custom_translation": False,
                }
            )

        return self.deduplicate_tags(tags)

    def normalize_tag_list(
        self,
        values: list,
    ) -> list[dict]:
        tags = []

        for item in values:
            if isinstance(item, str):
                original = item.strip()

                if original:
                    tags.append(
                        {
                            "original": original,
                            "translated": "",
                            "artwork_count": 0,
                            "custom_translation": False,
                        }
                    )

                continue

            if not isinstance(item, dict):
                continue

            original = str(
                item.get("tag")
                or item.get("name")
                or item.get("original")
                or ""
            ).strip()

            if not original:
                continue

            count = self.to_non_negative_int(
                item.get("cnt")
                or item.get("count")
                or item.get("total")
                or item.get("artwork_count")
                or 0
            )

            tags.append(
                {
                    "original": original,
                    "translated": self.extract_translated_tag(item),
                    "artwork_count": count,
                    "custom_translation": False,
                }
            )

        return tags

    def normalize_tag_dict(
        self,
        values: dict,
    ) -> list[dict]:
        tags = []

        for original, raw_value in values.items():
            original = str(original or "").strip()

            if not original:
                continue

            count = 0
            translated = ""

            if isinstance(raw_value, dict):
                translated = self.extract_translated_tag(raw_value)
                count = self.to_non_negative_int(
                    raw_value.get("cnt")
                    or raw_value.get("count")
                    or raw_value.get("total")
                    or raw_value.get("artwork_count")
                    or 0
                )
            elif isinstance(raw_value, int):
                count = raw_value

            tags.append(
                {
                    "original": original,
                    "translated": translated,
                    "artwork_count": count,
                    "custom_translation": False,
                }
            )

        return tags

    def extract_translated_tag(
        self,
        item: dict,
    ) -> str:
        translation = item.get("translation")

        if isinstance(translation, dict):
            for value in translation.values():
                text = str(value or "").strip()

                if text:
                    return text

        for key in (
            "tag_translation",
            "translated",
            "translated_name",
            "romaji",
        ):
            text = str(item.get(key, "") or "").strip()

            if text:
                return text

        return ""

    def deduplicate_tags(
        self,
        tags: list[dict],
    ) -> list[dict]:
        result = []
        seen = set()

        for tag in tags:
            original = str(tag.get("original", "") or "").strip()

            if not original or original in seen:
                continue

            seen.add(original)
            result.append(tag)

        return result

    def to_non_negative_int(
        self,
        value,
    ) -> int:
        try:
            return max(0, int(value))
        except (TypeError, ValueError):
            return 0
