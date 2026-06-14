from PySide6.QtWidgets import QFileDialog, QMessageBox

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
        section.rating_input.setText(
            str(to_int(artist.get("rating", 0), minimum=0, maximum=10))
        )
        section.status_label.setText(
            status_label(artist.get("status"))
        )
        section.update_status_label.setText(
            status_label(artist.get("update_status"))
        )
        section.folder_path_input.setText(
            display_value(artist.get("folder_path"))
        )
        section.memo_edit.setPlainText(
            str(artist.get("memo", "") or "")
        )

    def clear_artist(self):
        self.page.artist_id = None
        self.page.current_artist = None

        section = self.page.info_section

        section.artist_name_input.clear()
        section.pixiv_id_label.setText("-")
        section.artwork_count_input.clear()
        section.rating_input.clear()
        section.status_label.setText("-")
        section.update_status_label.setText("-")
        section.folder_path_input.clear()
        section.memo_edit.clear()

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
            rating = parse_rating(
                section.rating_input.text(),
            )
        except ValueError as error:
            self.show_warning(
                "입력 오류",
                str(error),
            )
            return

        folder_path = section.folder_path_input.text().strip()

        if folder_path == "-":
            folder_path = ""

        update_data = dict(self.page.current_artist)
        update_data["artist_name"] = artist_name
        update_data["folder_artwork_count"] = artwork_count
        update_data["rating"] = rating
        update_data["memo"] = section.memo_edit.toPlainText().strip()
        update_data["folder_path"] = folder_path

        try:
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

        self.page.current_artist = update_data
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
