import json

from .models import TagData
from .parser import TagParser


class TagService:
    def __init__(self):
        self.parser = TagParser()

    def parse_tags(
        self,
        raw_tags,
    ) -> list[TagData]:
        return self.parser.parse(raw_tags)

    def normalize_tags(
        self,
        raw_tags,
        sort_tags: bool = True,
    ) -> list[TagData]:
        tags = self.parse_tags(raw_tags)

        tag_map = {}
        ordered_keys = []

        for tag in tags:
            key = tag.original.casefold()

            if key not in tag_map:
                ordered_keys.append(key)
                tag_map[key] = TagData(
                    original=tag.original,
                    translated=tag.translated,
                    artwork_count=tag.artwork_count,
                    file_count=tag.file_count,
                    custom_translation=tag.custom_translation,
                )
                continue

            existing = tag_map[key]

            if not existing.translated and tag.translated:
                existing.translated = tag.translated

            existing.artwork_count += tag.artwork_count
            existing.file_count += tag.file_count
            existing.custom_translation = (
                existing.custom_translation
                or tag.custom_translation
            )

        normalized_tags = [
            tag_map[key]
            for key in ordered_keys
        ]

        if sort_tags:
            return self._sort_tags(normalized_tags)

        return normalized_tags

    def merge_tags(
        self,
        existing_tags,
        new_tags,
        sort_tags: bool = True,
        prefer_new_order: bool = False,
    ) -> list[TagData]:
        if prefer_new_order:
            return self._merge_tags_prefer_new_order(
                existing_tags=existing_tags,
                new_tags=new_tags,
                sort_tags=sort_tags,
            )

        existing = {
            tag.original.casefold(): tag
            for tag in self.normalize_tags(existing_tags, sort_tags=sort_tags)
        }

        incoming = self.normalize_tags(new_tags, sort_tags=sort_tags)

        for tag in incoming:
            key = tag.original.casefold()
            old_tag = existing.get(key)

            if old_tag is None:
                existing[key] = tag
                continue

            if old_tag.custom_translation:
                tag.translated = old_tag.translated
                tag.custom_translation = True
            elif not tag.translated and old_tag.translated:
                tag.translated = old_tag.translated

            tag.artwork_count = max(
                old_tag.artwork_count,
                tag.artwork_count,
            )
            tag.file_count = max(
                old_tag.file_count,
                tag.file_count,
            )

            existing[key] = tag

        result = list(existing.values())

        if sort_tags:
            return self._sort_tags(result)

        return result

    def serialize_tags(
        self,
        raw_tags,
        sort_tags: bool = True,
    ) -> str:
        tags = self.normalize_tags(
            raw_tags,
            sort_tags=sort_tags,
        )

        return json.dumps(
            [
                tag.to_dict()
                for tag in tags
            ],
            ensure_ascii=False,
        )

    def _merge_tags_prefer_new_order(
        self,
        existing_tags,
        new_tags,
        sort_tags: bool,
    ) -> list[TagData]:
        existing = {
            tag.original.casefold(): tag
            for tag in self.normalize_tags(existing_tags, sort_tags=False)
        }

        incoming = self.normalize_tags(new_tags, sort_tags=False)

        result = []
        used_keys = set()

        for tag in incoming:
            key = tag.original.casefold()
            old_tag = existing.get(key)

            if old_tag is not None:
                if old_tag.custom_translation:
                    tag.translated = old_tag.translated
                    tag.custom_translation = True
                elif not tag.translated and old_tag.translated:
                    tag.translated = old_tag.translated

                tag.artwork_count = max(
                    old_tag.artwork_count,
                    tag.artwork_count,
                )
                tag.file_count = max(
                    old_tag.file_count,
                    tag.file_count,
                )

            result.append(tag)
            used_keys.add(key)

        for key, old_tag in existing.items():
            if key not in used_keys:
                result.append(old_tag)

        if sort_tags:
            return self._sort_tags(result)

        return result

    def _sort_tags(
        self,
        tags: list[TagData],
    ) -> list[TagData]:
        tags.sort(
            key=lambda item: (
                item.artwork_count,
                item.file_count,
                item.original,
            ),
            reverse=True,
        )

        return tags
