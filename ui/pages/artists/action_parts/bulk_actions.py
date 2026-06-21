from PySide6.QtWidgets import QFileDialog, QInputDialog, QMessageBox

from app.database.connection import DATA_DIR


class ArtistsBulkActions:
    def handle_bulk_rating_change(self):
        artist_ids = self._get_selected_artist_ids()

        if not artist_ids:
            return

        self.handle_rating_change_for_artist_ids(artist_ids)

    def handle_rating_change_for_artist_ids(
        self,
        artist_ids: list[int],
    ):
        if not artist_ids:
            return

        rating_text, ok = QInputDialog.getText(
            self.page,
            "평점 변경",
            f"선택한 작가 {len(artist_ids)}명의 평점 입력 (0~10)",
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
                "변경 실패",
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

        self.handle_favorite_state_for_artist_ids(
            artist_ids,
            is_favorite,
        )

    def handle_favorite_state_for_artist_ids(
        self,
        artist_ids: list[int],
        is_favorite: bool,
    ):
        if not artist_ids:
            return

        try:
            self.page.artist_service.bulk_update_favorite(
                artist_ids,
                is_favorite,
            )
        except Exception as error:
            self.show_warning(
                "변경 실패",
                str(error),
            )
            return

        self.reload_artists_keep_selection(artist_ids)

    def handle_bulk_delete(self):
        artist_ids = self._get_selected_artist_ids()

        if not artist_ids:
            return

        self.handle_delete_for_artist_ids(artist_ids)

    def handle_delete_for_artist_ids(
        self,
        artist_ids: list[int],
    ):
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

            message += f"\n\n건너뛴 항목:\n{preview}"

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
