import json
import subprocess
import webbrowser
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QMessageBox,
    QPushButton,
    QTableWidgetItem,
    QWidget,
)

from .utils import (
    calculate_missing_artwork_ids,
    display_value,
    find_recent_local_artworks,
    folder_status_label,
    format_datetime,
    parse_id_text,
    parse_non_negative_int,
    parse_rating,
    status_label,
    to_int,
)


class ArtistDetailActions:
    PIXIV_ARTWORK_URL = "https://www.pixiv.net/artworks/{artwork_id}"

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

    def refresh_artist(self):
        if self.page.artist_id is None:
            self.clear_artist()
            return

        artist = self.page.artist_service.get_artist(self.page.artist_id)

        if artist is None:
            self.clear_artist()
            return

        self.page.current_artist = artist
        self.set_artist_data(artist)

    def rescan_artist(self):
        if self.page.artist_id is None:
            self.show_warning(
                "재스캔 오류",
                "재스캔할 작가 정보가 없습니다.",
            )
            return

        try:
            self.page.artist_service.rescan_artist_folder(
                self.page.artist_id,
            )
        except Exception as error:
            self.show_warning(
                "재스캔 오류",
                f"현재 작가를 재스캔하지 못했습니다.\n{error}",
            )
            return

        self.refresh_artist()
        self.page.artist_updated.emit(self.page.artist_id)

        self.show_information(
            "재스캔 완료",
            "현재 작가 폴더를 다시 스캔했습니다.",
        )

    def check_artist_update(self):
        if self.page.artist_id is None:
            self.show_warning(
                "업데이트 확인 오류",
                "업데이트를 확인할 작가 정보가 없습니다.",
            )
            return

        try:
            result = self.page.artist_service.check_artist_update(
                self.page.artist_id,
            )
        except Exception as error:
            self.show_warning(
                "업데이트 확인 오류",
                f"현재 작가의 업데이트를 확인하지 못했습니다.\n{error}",
            )
            return

        self.refresh_artist()
        self.page.artist_updated.emit(self.page.artist_id)

        missing_count = to_int(
            result.get("missing_count", 0),
            minimum=0,
        )
        status_text = status_label(result.get("status"))

        self.show_information(
            "업데이트 확인 완료",
            f"업데이트 상태: {status_text}\n누락 작품 수: {missing_count}",
        )

    def copy_folder_path(self):
        artist = self.page.current_artist

        if artist is None:
            return

        folder_path = str(artist.get("folder_path", "") or "").strip()

        if not folder_path:
            return

        QApplication.clipboard().setText(folder_path)

    def copy_pixiv_id(self):
        artist = self.page.current_artist

        if artist is None:
            return

        pixiv_id = str(artist.get("pixiv_id", "") or "").strip()

        if not pixiv_id:
            return

        QApplication.clipboard().setText(pixiv_id)

    def open_all_missing_artworks(self):
        artwork_ids = self.get_all_artwork_ids(
            self.page.info_section.missing_artwork_table,
            0,
        )

        self.open_pixiv_artworks(artwork_ids)

    def get_all_artwork_ids(self, table, column: int) -> list[str]:
        artwork_ids = []

        for row in range(table.rowCount()):
            item = table.item(row, column)

            if item is None:
                continue

            artwork_id = item.text().strip()

            if artwork_id:
                artwork_ids.append(artwork_id)

        return artwork_ids

    def open_pixiv_artwork(self, artwork_id: str):
        artwork_id = str(artwork_id or "").strip()

        if not artwork_id:
            return

        webbrowser.open(
            self.PIXIV_ARTWORK_URL.format(
                artwork_id=artwork_id,
            )
        )

    def open_pixiv_artworks(self, artwork_ids: list[str]):
        if not artwork_ids:
            return

        for artwork_id in artwork_ids:
            self.open_pixiv_artwork(artwork_id)

    def open_recent_artwork_folder(self, file_path: str):
        file_path = str(file_path or "").strip()

        if not file_path:
            return

        path = Path(file_path)

        if not path.exists():
            self.show_warning(
                "폴더 이동 오류",
                "파일을 찾을 수 없습니다.",
            )
            return

        try:
            subprocess.Popen(
                f'explorer.exe /select,"{path}"',
                shell=True,
            )
        except Exception:
            try:
                subprocess.Popen(
                    f'explorer.exe "{path.parent}"',
                    shell=True,
                )
            except Exception as error:
                self.show_warning(
                    "폴더 이동 오류",
                    f"파일 위치를 열지 못했습니다.\n{error}",
                )

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

        section.last_checked_at_label.setText(
            format_datetime(artist.get("last_checked_at"))
        )
        section.last_viewed_at_label.setText(
            format_datetime(artist.get("last_viewed_at"))
        )
        section.created_at_label.setText(
            format_datetime(artist.get("created_at"))
        )
        section.updated_at_label.setText(
            format_datetime(artist.get("updated_at"))
        )

        folder_path = display_value(artist.get("folder_path"))
        section.folder_path_input.setText(folder_path)
        section.folder_status_label.setText(
            folder_status_label(folder_path)
        )

        self.set_tag_table_data(
            artist.get("artist_tags", "")
        )
        self.set_missing_artwork_table_data(artist)
        self.set_recent_local_artwork_table_data(folder_path)

        section.memo_edit.setPlainText(
            str(artist.get("memo", "") or "")
        )
        section.reference_links_edit.setPlainText(
            str(artist.get("reference_links", "") or "")
        )
        section.download_note_edit.setPlainText(
            str(artist.get("download_note", "") or "")
        )

    def set_missing_artwork_table_data(self, artist: dict):
        section = self.page.info_section
        table = section.missing_artwork_table
        table.setRowCount(0)

        local_ids = parse_id_text(
            artist.get("local_latest_artwork_ids", "")
        )
        pixiv_ids = parse_id_text(
            artist.get("pixiv_latest_artwork_ids", "")
        )
        missing_ids = calculate_missing_artwork_ids(
            local_ids,
            pixiv_ids,
        )

        section.missing_artwork_count_label.setText(
            f"누락 작품 ID 목록 ({len(missing_ids)}개)"
        )

        for artwork_id in missing_ids:
            row = table.rowCount()
            table.insertRow(row)

            table.setItem(
                row,
                0,
                self.create_readonly_item(artwork_id),
            )

            pixiv_button = self.create_small_button("이동")
            pixiv_button.clicked.connect(
                lambda checked=False, aid=artwork_id: (
                    self.open_pixiv_artwork(aid)
                )
            )

            table.setCellWidget(
                row,
                1,
                self.create_centered_widget(pixiv_button),
            )

    def set_recent_local_artwork_table_data(self, folder_path: str):
        section = self.page.info_section
        table = section.recent_local_artwork_table
        table.setRowCount(0)

        artworks = find_recent_local_artworks(
            folder_path,
            limit=10,
        )

        for artwork in artworks:
            row = table.rowCount()
            table.insertRow(row)

            artwork_id = artwork["artwork_id"]
            file_path = artwork["file_path"]

            table.setItem(
                row,
                0,
                self.create_readonly_item(artwork_id),
            )
            table.setItem(
                row,
                1,
                self.create_readonly_item(str(artwork["file_count"])),
            )
            table.setItem(
                row,
                2,
                self.create_readonly_item(artwork["latest_modified_at"]),
            )

            pixiv_button = self.create_small_button("Pixiv")
            pixiv_button.clicked.connect(
                lambda checked=False, aid=artwork_id: (
                    self.open_pixiv_artwork(aid)
                )
            )

            folder_button = self.create_small_button("폴더")
            folder_button.clicked.connect(
                lambda checked=False, path=file_path: (
                    self.open_recent_artwork_folder(path)
                )
            )

            shortcut_widget = self.create_shortcut_widget(
                pixiv_button,
                folder_button,
            )

            table.setCellWidget(row, 3, shortcut_widget)

    def create_readonly_item(self, text: str) -> QTableWidgetItem:
        item = QTableWidgetItem(str(text))
        item.setFlags(item.flags() & ~Qt.ItemIsEditable)

        return item

    def create_small_button(self, text: str) -> QPushButton:
        button = QPushButton(text)
        button.setObjectName("smallActionButton")
        button.setCursor(Qt.PointingHandCursor)
        button.setFixedSize(60, 24)

        return button

    def create_centered_widget(self, widget) -> QWidget:
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addStretch()
        layout.addWidget(widget)
        layout.addStretch()

        return container

    def create_shortcut_widget(self, *buttons) -> QWidget:
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        layout.addStretch()

        for button in buttons:
            layout.addWidget(button)

        layout.addStretch()

        return container

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
        section.last_checked_at_label.setText("-")
        section.last_viewed_at_label.setText("-")
        section.created_at_label.setText("-")
        section.updated_at_label.setText("-")
        section.folder_status_label.setText("-")
        section.tag_table.setRowCount(0)
        section.missing_artwork_table.setRowCount(0)
        section.recent_local_artwork_table.setRowCount(0)
        section.missing_artwork_count_label.setText("누락 작품 ID 목록")
        section.folder_path_input.clear()
        section.memo_edit.clear()
        section.reference_links_edit.clear()
        section.download_note_edit.clear()

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
        self.page.info_section.folder_status_label.setText(
            folder_status_label(folder_path)
        )

        self.set_recent_local_artwork_table_data(folder_path)

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
            update_data["reference_links"] = (
                section.reference_links_edit.toPlainText().strip()
            )
            update_data["download_note"] = (
                section.download_note_edit.toPlainText().strip()
            )
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
