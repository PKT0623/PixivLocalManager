import json

from PySide6.QtWidgets import QFileDialog, QMessageBox, QTableWidgetItem

from .utils import (
    display_value,
    parse_non_negative_int,
    parse_rating,
    status_label,
    to_int,
)


class ArtistDetailActions:
    def __init__(self, page):
        self.page = page

    def set_artist(self, artist_id: int):
        self.page.artist_id = artist_id

        try:
            self.page.artist_service.update_last_viewed(artist_id)
        except Exception:
            pass

        artist = self.page.artist_service.get_artist(artist_id)

        if artist is None:
            self.clear_artist()
            return

        self.page.current_artist = artist
        self.set_artist_data(artist)

    def set_artist_data(self, artist: dict):
        section = self.page.info_section

        section.artist_name_input.setText(
            display_value(artist.get("artist_name"))
        )
        section.pixiv_id_label.setText(
            display_value(artist.get("pixiv_id"))
        )
        section.artwork_count_input.setText(
            str(to_int(artist.get("folder_artwork_count", 0)))
        )
        section.file_count_input.setText(
            str(to_int(artist.get("folder_file_count", 0)))
        )
        section.rating_input.setText(
            str(to_int(artist.get("rating", 0), minimum=0, maximum=10))
        )
        section.status_label.setText(
            status_label(artist.get("status"))
        )
        section.update_status_label.setText(
            status_label(artist.get("update_status"))
        )

        section.favorite_checkbox.setChecked(
            bool(artist.get("is_favorite", 0))
        )
        section.hidden_checkbox.setChecked(
            bool(artist.get("is_hidden", 0))
        )
        section.last_viewed_at_label.setText(
            display_value(artist.get("last_viewed_at"))
        )

        self.set_tag_table_data(
            artist.get("artist_tags", "")
        )

        section.folder_path_input.setText(
            display_value(artist.get("folder_path"))
        )
        section.memo_edit.setPlainText(
            str(artist.get("memo", "") or "")
        )

    def set_tag_table_data(self, artist_tags):
        section = self.page.info_section
        section.tag_table.setRowCount(0)

        tags = self.parse_artist_tags(artist_tags)

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
                }
            )

        return result

    def collect_tag_table_data(self) -> str:
        section = self.page.info_section
        tags = []

        for row in range(section.tag_table.rowCount()):
            name_item = section.tag_table.item(row, 0)
            translated_item = section.tag_table.item(row, 1)
            count_item = section.tag_table.item(row, 2)

            name = ""
            translated_name = ""
            artwork_count_text = "0"

            if name_item is not None:
                name = name_item.text().strip()

            if translated_item is not None:
                translated_name = translated_item.text().strip()

            if count_item is not None:
                artwork_count_text = count_item.text().strip()

            if not name and not translated_name:
                continue

            try:
                artwork_count = parse_non_negative_int(
                    artwork_count_text or "0",
                    "태그 작품 수",
                )
            except ValueError:
                raise ValueError(
                    f"{row + 1}번째 태그의 작품 수가 올바르지 않습니다."
                )

            tags.append(
                {
                    "name": name,
                    "translated_name": translated_name,
                    "artwork_count": artwork_count,
                }
            )

        tags.sort(
            key=lambda item: item.get("artwork_count", 0),
            reverse=True,
        )

        return json.dumps(
            tags,
            ensure_ascii=False,
        )

    def clear_artist(self):
        self.page.artist_id = None
        self.page.current_artist = None

        section = self.page.info_section

        section.artist_name_input.clear()
        section.pixiv_id_label.setText("-")
        section.artwork_count_input.clear()
        section.file_count_input.clear()
        section.rating_input.clear()
        section.status_label.setText("-")
        section.update_status_label.setText("-")
        section.favorite_checkbox.setChecked(False)
        section.hidden_checkbox.setChecked(False)
        section.last_viewed_at_label.setText("-")
        section.tag_table.setRowCount(0)
        section.folder_path_input.clear()
        section.memo_edit.clear()

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

    def select_folder(self):
        current_path = self.page.info_section.folder_path_input.text().strip()

        if current_path == "-":
            current_path = ""

        folder_path = QFileDialog.getExistingDirectory(
            self.page,
            "작가 폴더 선택",
            current_path,
        )

        if not folder_path:
            return

        self.page.info_section.folder_path_input.setText(folder_path)

    def save_artist(self):
        if self.page.artist_id is None or self.page.current_artist is None:
            self.show_warning(
                "저장 오류",
                "저장할 작가 정보가 없습니다.",
            )
            return

        section = self.page.info_section
        artist_name = section.artist_name_input.text().strip()

        if not artist_name:
            self.show_warning(
                "입력 오류",
                "작가명은 비워둘 수 없습니다.",
            )
            return

        try:
            artwork_count = parse_non_negative_int(
                section.artwork_count_input.text(),
                "작품 수",
            )
            file_count = parse_non_negative_int(
                section.file_count_input.text(),
                "파일 수",
            )
            rating = parse_rating(
                section.rating_input.text(),
            )
            artist_tags = self.collect_tag_table_data()
        except ValueError as error:
            self.show_warning(
                "입력 오류",
                str(error),
            )
            return

        folder_path = section.folder_path_input.text().strip()

        if folder_path == "-":
            folder_path = ""

        previous_folder_path = str(
            self.page.current_artist.get("folder_path", "") or ""
        ).strip()

        try:
            if folder_path and folder_path != previous_folder_path:
                self.page.current_artist = (
                    self.page.artist_service.change_artist_folder(
                        self.page.artist_id,
                        folder_path,
                    )
                )

            update_data = dict(self.page.current_artist)
            update_data["artist_name"] = artist_name
            update_data["folder_artwork_count"] = artwork_count
            update_data["folder_file_count"] = file_count
            update_data["rating"] = rating
            update_data["is_favorite"] = int(
                section.favorite_checkbox.isChecked()
            )
            update_data["is_hidden"] = int(section.hidden_checkbox.isChecked())
            update_data["artist_tags"] = artist_tags
            update_data["memo"] = section.memo_edit.toPlainText().strip()
            update_data["folder_path"] = folder_path

            self.page.artist_service.update_artist(
                self.page.artist_id,
                update_data,
            )
        except Exception as error:
            self.show_warning(
                "저장 오류",
                f"작가 정보를 저장하지 못했습니다.\n{error}",
            )
            return

        self.page.current_artist = self.page.artist_service.get_artist(
            self.page.artist_id
        )

        if self.page.current_artist is not None:
            self.set_artist_data(self.page.current_artist)

        self.page.artist_updated.emit(self.page.artist_id)

        self.show_information(
            "저장 완료",
            "작가 정보가 저장되었습니다.",
        )

    def show_information(self, title: str, message: str):
        message_box = QMessageBox(self.page)
        message_box.setIcon(QMessageBox.NoIcon)
        message_box.setWindowTitle(title)
        message_box.setText(message)
        message_box.setStandardButtons(QMessageBox.Ok)
        message_box.exec()

    def show_warning(self, title: str, message: str):
        message_box = QMessageBox(self.page)
        message_box.setIcon(QMessageBox.NoIcon)
        message_box.setWindowTitle(title)
        message_box.setText(message)
        message_box.setStandardButtons(QMessageBox.Ok)
        message_box.exec()
