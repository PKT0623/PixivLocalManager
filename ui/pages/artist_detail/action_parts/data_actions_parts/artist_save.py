from ...utils import (
    parse_non_negative_int,
    parse_rating,
)


class ArtistSaveActions:
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

        self.show_status_message("작가 정보가 저장되었습니다.")
