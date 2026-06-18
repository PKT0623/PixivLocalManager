import json

from .models import TagData


EMPTY_VALUES = {
    "",
    "[]",
    "{}",
    "null",
    "none",
}


class TagParser:
    def parse(self, raw_tags) -> list[TagData]:
        if raw_tags is None:
            return []

        if isinstance(raw_tags, list):
            return self._parse_list(raw_tags)

        text = str(raw_tags).strip()

        if text.lower() in EMPTY_VALUES:
            return []

        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            return self._parse_legacy_string(text)

        if not isinstance(parsed, list):
            return []

        return self._parse_list(parsed)

    def _parse_list(
        self,
        items: list,
    ) -> list[TagData]:
        result = []

        for item in items:
            if isinstance(item, TagData):
                result.append(
                    TagData(
                        original=item.original,
                        translated=item.translated,
                        artwork_count=item.artwork_count,
                        file_count=item.file_count,
                        custom_translation=item.custom_translation,
                    )
                )
                continue

            if isinstance(item, str):
                tag_name = item.strip()

                if tag_name:
                    result.append(
                        TagData(
                            original=tag_name,
                        )
                    )

                continue

            if not isinstance(item, dict):
                continue

            result.append(
                TagData(
                    original=self._get_original(item),
                    translated=self._get_translated(item),
                    artwork_count=self._to_int(
                        item.get("artwork_count")
                        or item.get("count")
                        or item.get("cnt")
                        or 0
                    ),
                    file_count=self._to_int(
                        item.get("file_count")
                        or 0
                    ),
                    custom_translation=bool(
                        item.get("custom_translation", False)
                    ),
                )
            )

        return [
            tag
            for tag in result
            if tag.original
        ]

    def _parse_legacy_string(
        self,
        text: str,
    ) -> list[TagData]:
        result = []

        for tag_name in text.replace("\n", ",").split(","):
            tag_name = tag_name.strip()

            if not tag_name:
                continue

            result.append(
                TagData(
                    original=tag_name,
                )
            )

        return result

    def _get_original(
        self,
        item: dict,
    ) -> str:
        return str(
            item.get("original")
            or item.get("name")
            or item.get("tag")
            or ""
        ).strip()

    def _get_translated(
        self,
        item: dict,
    ) -> str:
        return str(
            item.get("translated")
            or item.get("translated_name")
            or item.get("tag_translation")
            or ""
        ).strip()

    def _to_int(
        self,
        value,
    ) -> int:
        try:
            return max(0, int(value))
        except (TypeError, ValueError):
            return 0
