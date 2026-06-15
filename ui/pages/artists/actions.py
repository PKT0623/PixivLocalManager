from PySide6.QtWidgets import QFileDialog, QInputDialog, QMessageBox

from app.database.connection import DATA_DIR
from ui.dialogs.update_check import UpdateCheckDialog

from .filters import (
    DEFAULT_SORT_REVERSE,
    filter_artists,
    sort_artists,
)


MAX_SORT_RULES = 3


class ArtistsActions:
    def __init__(self, page):
        self.page = page

    def load_artists(self):
        self.page.all_artists = self.page.artist_service.get_all_artists()
        self.apply_filter_and_sort()

    def reload_artists_keep_selection(
        self,
        artist_ids: list[int],
    ):
        self.load_artists()
        self.page.artist_table.select_artist_ids(artist_ids)
        self.page.artist_table.setFocus()

    def apply_filter_and_sort(self, *args):
        toolbar = self.page.toolbar

        artists = filter_artists(
            self.page.all_artists,
            keyword=toolbar.search_input.text(),
            rating_value=toolbar.get_rating_filter_value(),
            rating_filter_mode=toolbar.get_rating_filter_mode(),
            favorite_only=toolbar.favorite_only_checkbox.isChecked(),
            update_required_only=(
                toolbar.update_required_only_checkbox.isChecked()
            ),
            unknown_only=toolbar.unknown_only_checkbox.isChecked(),
            unrated_only=toolbar.unrated_only_checkbox.isChecked(),
            exclude_hidden=toolbar.exclude_hidden_checkbox.isChecked(),
        )

        artists = sort_artists(
            artists,
            self.page.sort_rules,
        )

        self.page.artist_table.set_artists(artists)
        self.page.artist_table.set_sort_indicators(
            self.page.sort_rules,
        )

    def reset_filters(self):
        self.page.toolbar.reset_filter_values()
        self.apply_filter_and_sort()

    def reset_sort(self):
        self.page.sort_rules = self.page.default_sort_rules.copy()
        self.apply_filter_and_sort()

    def toggle_rating_filter_mode(self):
        self.page.toolbar.toggle_rating_filter_mode()
        self.apply_filter_and_sort()

    def open_update_check_dialog(self):
        dialog = UpdateCheckDialog(
            self.page.all_artists,
            self.page,
        )
        dialog.update_finished.connect(self.load_artists)
        dialog.exec()

        self.load_artists()

    def handle_sort_requested(
        self,
        sort_field: str,
        is_multi_sort: bool,
    ):
        if is_multi_sort:
            self._handle_multi_sort_requested(sort_field)
        else:
            self._handle_single_sort_requested(sort_field)

        self.apply_filter_and_sort()

    def _handle_single_sort_requested(self, sort_field: str):
        current_rule = self._find_sort_rule(sort_field)

        if current_rule is None or len(self.page.sort_rules) > 1:
            sort_reverse = DEFAULT_SORT_REVERSE.get(
                sort_field,
                False,
            )
        else:
            sort_reverse = not current_rule[1]

        self.page.sort_rules = [
            (
                sort_field,
                sort_reverse,
            )
        ]

    def _handle_multi_sort_requested(self, sort_field: str):
        sort_rules = self.page.sort_rules.copy()

        for index, rule in enumerate(sort_rules):
            if rule[0] != sort_field:
                continue

            sort_rules[index] = (
                sort_field,
                not rule[1],
            )
            self.page.sort_rules = sort_rules
            return

        sort_rules.append(
            (
                sort_field,
                DEFAULT_SORT_REVERSE.get(
                    sort_field,
                    False,
                ),
            )
        )

        if len(sort_rules) > MAX_SORT_RULES:
            sort_rules = sort_rules[-MAX_SORT_RULES:]

        self.page.sort_rules = sort_rules

    def _find_sort_rule(
        self,
        sort_field: str,
    ) -> tuple[str, bool] | None:
        for rule in self.page.sort_rules:
            if rule[0] == sort_field:
                return rule

        return None

    def toggle_rating_display(self):
        if self.page.rating_display_mode == "stars":
            self.page.rating_display_mode = "number"
            self.page.toolbar.rating_toggle_button.setText("평점: 숫자")
        else:
            self.page.rating_display_mode = "stars"
            self.page.toolbar.rating_toggle_button.setText("평점: 별")

        self.page.artist_table.set_rating_display_mode(
            self.page.rating_display_mode
        )

    def handle_favorite_toggled(
        self,
        artist_id: int,
    ):
        try:
            self.page.artist_service.toggle_favorite(
                artist_id
            )
        except Exception as error:
            print(error)
            return

        self.load_artists()

    def handle_rating_changed(
        self,
        artist_id: int,
        rating: int,
    ):
        try:
            self.page.artist_service.update_rating(
                artist_id,
                rating,
            )
        except Exception as error:
            print(error)
            return

        self.reload_artists_keep_selection([artist_id])

    def handle_bulk_rating_change(self):
        artist_ids = self._get_selected_artist_ids()

        if not artist_ids:
            return

        rating_text, ok = QInputDialog.getText(
            self.page,
            "평점 일괄 변경",
            "선택한 작가의 평점 입력 (0~10)",
        )

        if not ok:
            return

        rating_text = rating_text.strip()

        if not rating_text:
            return

        try:
            rating = int(rating_text)
        except ValueError:
            self.show_warning(
                "입력 오류",
                "평점은 숫자로 입력해야 합니다.",
            )
            return

        if rating < 0 or rating > 10:
            self.show_warning(
                "입력 오류",
                "평점은 0~10 사이여야 합니다.",
            )
            return

        try:
            self.page.artist_service.bulk_update_rating(
                artist_ids,
                rating,
            )
        except Exception as error:
            self.show_warning(
                "일괄 변경 실패",
                str(error),
            )
            return

        self.reload_artists_keep_selection(artist_ids)

    def handle_bulk_favorite(self):
        self._handle_bulk_favorite_state(True)

    def handle_bulk_unfavorite(self):
        self._handle_bulk_favorite_state(False)

    def _handle_bulk_favorite_state(self, is_favorite: bool):
        artist_ids = self._get_selected_artist_ids()

        if not artist_ids:
            return

        try:
            self.page.artist_service.bulk_update_favorite(
                artist_ids,
                is_favorite,
            )
        except Exception as error:
            self.show_warning(
                "일괄 변경 실패",
                str(error),
            )
            return

        self.reload_artists_keep_selection(artist_ids)

    def handle_bulk_hide(self):
        self._handle_bulk_hidden_state(True)

    def handle_bulk_unhide(self):
        self._handle_bulk_hidden_state(False)

    def _handle_bulk_hidden_state(self, is_hidden: bool):
        artist_ids = self._get_selected_artist_ids()

        if not artist_ids:
            return

        try:
            self.page.artist_service.bulk_update_hidden(
                artist_ids,
                is_hidden,
            )
        except Exception as error:
            self.show_warning(
                "일괄 변경 실패",
                str(error),
            )
            return

        self.reload_artists_keep_selection(artist_ids)

    def handle_bulk_delete(self):
        artist_ids = self._get_selected_artist_ids()

        if not artist_ids:
            return

        result = QMessageBox.question(
            self.page,
            "작가 삭제",
            (
                f"선택한 작가 {len(artist_ids)}명을 삭제할까요?\n\n"
                "삭제 전에 자동 백업이 생성됩니다."
            ),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if result != QMessageBox.Yes:
            return

        try:
            self.page.artist_service.delete_artists(
                artist_ids
            )
        except Exception as error:
            self.show_warning(
                "삭제 실패",
                str(error),
            )
            return

        self.load_artists()

    def handle_restore_deleted_artists(self):
        backup_dir = DATA_DIR / "backups" / "deleted_artists"
        backup_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        file_path, _ = QFileDialog.getOpenFileName(
            self.page,
            "삭제 작가 백업 파일 선택",
            str(backup_dir),
            "JSON Files (*.json);;All Files (*)",
        )

        if not file_path:
            return

        try:
            result = self.page.artist_service.restore_deleted_artists_backup(
                file_path
            )
        except Exception as error:
            self.show_warning(
                "복구 실패",
                str(error),
            )
            return

        self.load_artists()
        self.show_information(
            "복구 완료",
            self._format_restore_result(result),
        )

    def _format_restore_result(self, result: dict) -> str:
        message = (
            f"복구 시도: {result.get('total_count', 0)}명\n"
            f"복구 완료: {result.get('restored_count', 0)}명\n"
            f"건너뜀: {result.get('skipped_count', 0)}명"
        )

        skipped_artists = result.get("skipped_artists", [])

        if skipped_artists:
            preview_items = skipped_artists[:5]
            preview = "\n".join(
                (
                    f"- {item.get('artist_name', '-')}"
                    f" / {item.get('pixiv_id', '-')}"
                    f" / {item.get('reason', '-')}"
                )
                for item in preview_items
            )

            message += f"\n\n건너뜬 항목:\n{preview}"

            if len(skipped_artists) > len(preview_items):
                message += "\n..."

        return message

    def _get_selected_artist_ids(self) -> list[int]:
        artist_ids = self.page.artist_table.get_selected_artist_ids()

        if artist_ids:
            return artist_ids

        self.show_information(
            "선택 필요",
            "작가를 하나 이상 선택하세요.",
        )

        return []

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
