from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTableWidgetItem

from app.database import ArtistUpdateHistoryRepository

from ..utils import (
    display_value,
    folder_status_label,
    format_datetime,
    parse_non_negative_int,
    parse_id_text,
    parse_rating,
    status_label,
    to_int,
)


class ArtistDataActions:
    UPDATE_HISTORY_LIMIT = 20

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
        self.set_update_history_table_data(artist.get("id"))

        section.memo_edit.setPlainText(
            str(artist.get("memo", "") or "")
        )
        section.reference_links_edit.setPlainText(
            str(artist.get("reference_links", "") or "")
        )
        section.download_note_edit.setPlainText(
            str(artist.get("download_note", "") or "")
        )

    def set_update_history_table_data(
        self,
        artist_id,
    ):
        section = self.page.info_section
        table = section.update_history_table

        table.setRowCount(0)
        section.update_history_label.setText("업데이트 이력")
        section.update_history_summary_label.setText("최근 누락 변화: -")

        if artist_id is None:
            return

        histories = self._get_update_history_repo().get_by_artist_id_with_comparison(
            artist_id=artist_id,
            limit=self.UPDATE_HISTORY_LIMIT,
        )

        section.update_history_label.setText(
            f"업데이트 이력 ({len(histories)}건)"
        )

        if not histories:
            return

        self._set_update_history_summary(histories[0])

        for history in histories:
            self._add_update_history_row(history)

    def _add_update_history_row(
        self,
        history: dict,
    ):
        table = self.page.info_section.update_history_table

        row = table.rowCount()
        table.insertRow(row)

        values = [
            format_datetime(history.get("checked_at")),
            self._history_result_label(history),
            str(to_int(history.get("local_count", 0))),
            str(to_int(history.get("pixiv_count", 0))),
            str(to_int(history.get("missing_count", 0))),
            self._missing_delta_text(history),
            self._changed_ids_summary_text(history),
            self._history_detail_text(history),
        ]

        for column, value in enumerate(values):
            item = self._create_history_item(value)

            if column in (2, 3, 4, 5, 6):
                item.setTextAlignment(Qt.AlignCenter)

            table.setItem(row, column, item)

    def _set_update_history_summary(
        self,
        latest_history: dict,
    ):
        summary_label = self.page.info_section.update_history_summary_label

        if not latest_history.get("has_previous"):
            summary_label.setText("최근 누락 변화: 비교 이력 없음")
            return

        delta = to_int(latest_history.get("missing_delta", 0))

        if delta > 0:
            summary_label.setText(f"최근 누락 증가: +{delta}개")
            return

        if delta < 0:
            summary_label.setText(f"최근 누락 감소: {delta}개")
            return

        summary_label.setText("최근 누락 변화: 변화 없음")

    def _history_result_label(
        self,
        history: dict,
    ) -> str:
        result_label = str(history.get("result_label", "") or "").strip()

        if result_label:
            return result_label

        return status_label(history.get("result_status"))

    def _missing_delta_text(
        self,
        history: dict,
    ) -> str:
        if not history.get("has_previous"):
            return "-"

        delta = to_int(history.get("missing_delta", 0))

        if delta > 0:
            return f"+{delta} 증가"

        if delta < 0:
            return f"{delta} 감소"

        return "변화 없음"

    def _changed_ids_summary_text(
        self,
        history: dict,
    ) -> str:
        if not history.get("has_previous"):
            return "-"

        new_count = to_int(history.get("new_missing_count", 0))
        resolved_count = to_int(history.get("resolved_missing_count", 0))

        return f"신규 {new_count} / 해결 {resolved_count}"

    def _history_detail_text(
        self,
        history: dict,
    ) -> str:
        error_message = str(history.get("error_message", "") or "").strip()
        error_reason = str(history.get("error_reason", "") or "").strip()

        if error_message and error_reason:
            return f"{error_reason}: {error_message}"

        if error_message:
            return error_message

        if error_reason:
            return error_reason

        new_missing_ids = parse_id_text(history.get("new_missing_ids", ""))
        resolved_missing_ids = parse_id_text(
            history.get("resolved_missing_ids", "")
        )

        detail_parts = []

        if new_missing_ids:
            detail_parts.append(
                "신규 누락: " + ", ".join(new_missing_ids[:10])
            )

        if resolved_missing_ids:
            detail_parts.append(
                "해결됨: " + ", ".join(resolved_missing_ids[:10])
            )

        return " / ".join(detail_parts)

    def _create_history_item(
        self,
        text: str,
    ) -> QTableWidgetItem:
        item = QTableWidgetItem(str(text or ""))
        item.setFlags(item.flags() & ~Qt.ItemIsEditable)

        return item

    def _get_update_history_repo(self) -> ArtistUpdateHistoryRepository:
        if not hasattr(self, "update_history_repo"):
            self.update_history_repo = ArtistUpdateHistoryRepository()

        return self.update_history_repo

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
        section.update_history_table.setRowCount(0)
        section.missing_artwork_count_label.setText("누락 작품 ID 목록")
        section.update_history_label.setText("업데이트 이력")
        section.update_history_summary_label.setText("최근 누락 변화: -")
        section.folder_path_input.clear()
        section.memo_edit.clear()
        section.reference_links_edit.clear()
        section.download_note_edit.clear()

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
