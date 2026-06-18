import json

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTableWidgetItem

from ..utils import (
    parse_non_negative_int,
    to_int,
)


class ArtistTagActions:
    def set_tag_table_data(self, artist_tags):
        section = self.page.info_section
        section.tag_table.setRowCount(0)

        tags = self.normalize_tags(
            self.parse_artist_tags(artist_tags)
        )

        for tag in tags:
            row = section.tag_table.rowCount()
            section.tag_table.insertRow(row)

            original_item = QTableWidgetItem(
                str(tag.get("original", ""))
            )
            original_item.setFlags(
                original_item.flags()
                & ~Qt.ItemIsEditable
            )

            section.tag_table.setItem(
                row,
                0,
                original_item,
            )

            section.tag_table.setItem(
                row,
                1,
                QTableWidgetItem(
                    str(tag.get("translated", ""))
                ),
            )

            section.tag_table.setItem(
                row,
                2,
                QTableWidgetItem(
                    str(tag.get("artwork_count", 0))
                ),
            )

    def parse_artist_tags(self, artist_tags) -> list[dict]:
        if not artist_tags:
            return []

        if isinstance(artist_tags, list):
            parsed = artist_tags
        else:
            try:
                parsed = json.loads(str(artist_tags))
            except json.JSONDecodeError:
                return self.parse_legacy_tags(
                    str(artist_tags)
                )

        if not isinstance(parsed, list):
            return []

        result = []

        for item in parsed:
            if not isinstance(item, dict):
                continue

            result.append(
                {
                    "original": str(
                        item.get("original")
                        or item.get("name")
                        or ""
                    ).strip(),
                    "translated": str(
                        item.get("translated")
                        or item.get("translated_name")
                        or ""
                    ).strip(),
                    "artwork_count": to_int(
                        item.get("artwork_count")
                        or item.get("count")
                        or 0,
                        minimum=0,
                    ),
                    "custom_translation": bool(
                        item.get(
                            "custom_translation",
                            False,
                        )
                    ),
                }
            )

        return result

    def parse_legacy_tags(
        self,
        artist_tags: str,
    ) -> list[dict]:
        result = []

        for tag_name in artist_tags.replace("\n", ",").split(","):
            tag_name = tag_name.strip()

            if not tag_name:
                continue

            result.append(
                {
                    "original": tag_name,
                    "translated": "",
                    "artwork_count": 0,
                    "custom_translation": False,
                }
            )

        return result

    def collect_tag_table_rows(self) -> list[dict]:
        section = self.page.info_section
        tags = []

        for row in range(section.tag_table.rowCount()):
            original_item = section.tag_table.item(row, 0)
            translated_item = section.tag_table.item(row, 1)
            artwork_count_item = section.tag_table.item(row, 2)

            original = ""
            translated = ""
            artwork_count_text = "0"

            if original_item is not None:
                original = original_item.text().strip()

            if translated_item is not None:
                translated = translated_item.text().strip()

            if artwork_count_item is not None:
                artwork_count_text = (
                    artwork_count_item.text().strip()
                )

            if not original:
                continue

            try:
                artwork_count = parse_non_negative_int(
                    artwork_count_text or "0",
                    "태그 작품 수",
                )
            except ValueError:
                raise ValueError(
                    f"{row + 1}번째 태그의 수치가 "
                    "올바르지 않습니다."
                )

            tags.append(
                {
                    "original": original,
                    "translated": translated,
                    "artwork_count": artwork_count,
                    "custom_translation": bool(
                        translated
                    ),
                }
            )

        return tags

    def normalize_tags(
        self,
        tags: list[dict],
    ) -> list[dict]:
        normalized_map = {}

        for tag in tags:
            original = str(
                tag.get("original", "")
                or ""
            ).strip()

            translated = str(
                tag.get("translated", "")
                or ""
            ).strip()

            if not original:
                continue

            key = original.casefold()

            artwork_count = to_int(
                tag.get("artwork_count", 0),
                minimum=0,
            )

            custom_translation = bool(
                tag.get(
                    "custom_translation",
                    False,
                )
            )

            if key not in normalized_map:
                normalized_map[key] = {
                    "original": original,
                    "translated": translated,
                    "artwork_count": artwork_count,
                    "custom_translation": custom_translation,
                }
                continue

            existing = normalized_map[key]

            if not existing["translated"] and translated:
                existing["translated"] = translated

            existing["artwork_count"] += artwork_count
            existing["custom_translation"] = (
                existing["custom_translation"]
                or custom_translation
            )

        tags = list(normalized_map.values())

        tags.sort(
            key=lambda item: (
                item.get("artwork_count", 0),
                item.get("original", ""),
            ),
            reverse=True,
        )

        return tags

    def collect_tag_table_data(self) -> str:
        tags = self.normalize_tags(
            self.collect_tag_table_rows()
        )

        return json.dumps(
            tags,
            ensure_ascii=False,
        )

    def clean_tag_table(self):
        try:
            tags = self.normalize_tags(
                self.collect_tag_table_rows()
            )
        except ValueError as error:
            self.show_warning(
                "태그 정리 오류",
                str(error),
            )
            return

        self.set_tag_table_data(tags)

    def sort_tag_table(self):
        try:
            tags = self.collect_tag_table_rows()
        except ValueError as error:
            self.show_warning(
                "태그 정렬 오류",
                str(error),
            )
            return

        tags.sort(
            key=lambda item: (
                item.get("artwork_count", 0),
                item.get("original", ""),
            ),
            reverse=True,
        )

        self.set_tag_table_data(tags)

    def add_tag_row(self):
        self.page.info_section.add_empty_tag_row()

    def remove_selected_tag_row(self):
        table = self.page.info_section.tag_table
        selected_rows = (
            table.selectionModel()
            .selectedRows()
        )

        if not selected_rows:
            return

        for model_index in sorted(
            selected_rows,
            key=lambda index: index.row(),
            reverse=True,
        ):
            table.removeRow(
                model_index.row()
            )
