import json

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

            section.tag_table.setItem(
                row,
                0,
                QTableWidgetItem(str(tag.get("name", ""))),
            )
            section.tag_table.setItem(
                row,
                1,
                QTableWidgetItem(str(tag.get("translated_name", ""))),
            )
            section.tag_table.setItem(
                row,
                2,
                QTableWidgetItem(str(tag.get("artwork_count", 0))),
            )
            section.tag_table.setItem(
                row,
                3,
                QTableWidgetItem(str(tag.get("file_count", 0))),
            )

    def parse_artist_tags(self, artist_tags) -> list[dict]:
        if not artist_tags:
            return []

        if isinstance(artist_tags, list):
            return artist_tags

        try:
            parsed = json.loads(str(artist_tags))
        except json.JSONDecodeError:
            return self.parse_legacy_tags(str(artist_tags))

        if not isinstance(parsed, list):
            return []

        result = []

        for item in parsed:
            if not isinstance(item, dict):
                continue

            result.append(
                {
                    "name": str(item.get("name", "")).strip(),
                    "translated_name": str(
                        item.get("translated_name", "")
                    ).strip(),
                    "artwork_count": to_int(
                        item.get("artwork_count", 0),
                        minimum=0,
                    ),
                    "file_count": to_int(
                        item.get("file_count", 0),
                        minimum=0,
                    ),
                }
            )

        return result

    def parse_legacy_tags(self, artist_tags: str) -> list[dict]:
        result = []

        for tag_name in artist_tags.split(","):
            tag_name = tag_name.strip()

            if not tag_name:
                continue

            result.append(
                {
                    "name": tag_name,
                    "translated_name": "",
                    "artwork_count": 0,
                    "file_count": 0,
                }
            )

        return result

    def collect_tag_table_rows(self) -> list[dict]:
        section = self.page.info_section
        tags = []

        for row in range(section.tag_table.rowCount()):
            name_item = section.tag_table.item(row, 0)
            translated_item = section.tag_table.item(row, 1)
            artwork_count_item = section.tag_table.item(row, 2)
            file_count_item = section.tag_table.item(row, 3)

            name = ""
            translated_name = ""
            artwork_count_text = "0"
            file_count_text = "0"

            if name_item is not None:
                name = name_item.text().strip()

            if translated_item is not None:
                translated_name = translated_item.text().strip()

            if artwork_count_item is not None:
                artwork_count_text = artwork_count_item.text().strip()

            if file_count_item is not None:
                file_count_text = file_count_item.text().strip()

            if not name:
                continue

            try:
                artwork_count = parse_non_negative_int(
                    artwork_count_text or "0",
                    "태그 작품 수",
                )
                file_count = parse_non_negative_int(
                    file_count_text or "0",
                    "태그 파일 수",
                )
            except ValueError:
                raise ValueError(
                    f"{row + 1}번째 태그의 수치가 올바르지 않습니다."
                )

            tags.append(
                {
                    "name": name,
                    "translated_name": translated_name,
                    "artwork_count": artwork_count,
                    "file_count": file_count,
                }
            )

        return tags

    def normalize_tags(self, tags: list[dict]) -> list[dict]:
        normalized_map = {}

        for tag in tags:
            name = str(tag.get("name", "") or "").strip()
            translated_name = str(
                tag.get("translated_name", "") or ""
            ).strip()

            if not name:
                continue

            key = name.casefold()

            artwork_count = to_int(
                tag.get("artwork_count", 0),
                minimum=0,
            )
            file_count = to_int(
                tag.get("file_count", 0),
                minimum=0,
            )

            if key not in normalized_map:
                normalized_map[key] = {
                    "name": name,
                    "translated_name": translated_name,
                    "artwork_count": artwork_count,
                    "file_count": file_count,
                }
                continue

            existing_tag = normalized_map[key]

            if not existing_tag["translated_name"] and translated_name:
                existing_tag["translated_name"] = translated_name

            existing_tag["artwork_count"] += artwork_count
            existing_tag["file_count"] += file_count

        tags = list(normalized_map.values())

        tags.sort(
            key=lambda item: (
                item.get("artwork_count", 0),
                item.get("file_count", 0),
                item.get("name", ""),
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
                item.get("file_count", 0),
                item.get("name", ""),
            ),
            reverse=True,
        )

        self.set_tag_table_data(tags)

    def add_tag_row(self):
        self.page.info_section.add_empty_tag_row()

    def remove_selected_tag_row(self):
        table = self.page.info_section.tag_table
        selected_rows = table.selectionModel().selectedRows()

        if not selected_rows:
            return

        for model_index in sorted(
            selected_rows,
            key=lambda index: index.row(),
            reverse=True,
        ):
            table.removeRow(model_index.row())
