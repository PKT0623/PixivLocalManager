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
    ) -> list[TagData]:
        tags = self.parse_tags(raw_tags)

        tag_map = {}

        for tag in tags:
            key = tag.original.casefold()

            if key not in tag_map:
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

        return self._sort_tags(list(tag_map.values()))

    def merge_tags(
        self,
        existing_tags,
        new_tags,
    ) -> list[TagData]:
        existing = {
            tag.original.casefold(): tag
            for tag in self.normalize_tags(existing_tags)
        }

        incoming = self.normalize_tags(new_tags)

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

        return self._sort_tags(list(existing.values()))

    def serialize_tags(
        self,
        raw_tags,
    ) -> str:
        tags = self.normalize_tags(raw_tags)

        return json.dumps(
            [
                tag.to_dict()
                for tag in tags
            ],
            ensure_ascii=False,
        )

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
