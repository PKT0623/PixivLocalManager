from datetime import datetime
from math import ceil
from pathlib import Path

from PySide6.QtCore import QObject, QThread, Slot
from PySide6.QtWidgets import QFileDialog

from app.services import BookmarkService, FollowService, SettingsService

from .worker import PixivImportWorker


class PixivManagerActions(QObject):
    PAGE_SIZE_SETTING_KEY = "pixiv_manager_page_size"

    def __init__(self, page):
        super().__init__(page)

        self.page = page
        self.follow_service = FollowService()
        self.bookmark_service = BookmarkService()
        self.settings_service = SettingsService()

        self.follow_users = []
        self.bookmark_artworks = []

        self.current_page = 1
        self.filtered_items = []

    def load_saved_page_size(self):
        saved_page_size = self.settings_service.get_setting(
            self.PAGE_SIZE_SETTING_KEY
        )

        if not saved_page_size:
            return

        index = self.page.page_size_combo.findText(str(saved_page_size))

        if index < 0:
            return

        self.page.page_size_combo.blockSignals(True)
        self.page.page_size_combo.setCurrentIndex(index)
        self.page.page_size_combo.blockSignals(False)

    def handle_page_size_changed(self):
        page_size = self.page.page_size_combo.currentText()

        try:
            self.settings_service.set_setting(
                self.PAGE_SIZE_SETTING_KEY,
                page_size,
            )
        except Exception:
            pass

        self.reset_page_and_apply_filters()

    def load_data(self):
        self.follow_users = self.follow_service.get_all_follow_users()
        self.bookmark_artworks = self.bookmark_service.get_all_bookmark_artworks()

        self.page.summary_section.update_summary(
            self._build_summary(
                follow_users=self.follow_users,
                bookmark_artworks=self.bookmark_artworks,
            )
        )

        self.apply_filters()

        self.page.status_label.setText(
            "Pixiv 관리 데이터를 새로고침했습니다."
        )

    def reset_page_and_apply_filters(self):
        self.current_page = 1
        self.apply_filters()

    def apply_filters(self):
        source_items, id_field = self._get_current_source_items()
        self.filtered_items = self._filter_items(
            items=source_items,
            id_field=id_field,
        )

        page_items = self._get_current_page_items(self.filtered_items)
        self._load_current_table(page_items)
        self._update_page_labels(
            total_count=len(source_items),
            filtered_count=len(self.filtered_items),
            page_count=len(page_items),
        )

    def prev_page(self):
        if self.current_page <= 1:
            return

        self.current_page -= 1
        self.apply_filters()

    def next_page(self):
        max_page = self._get_max_page(len(self.filtered_items))

        if self.current_page >= max_page:
            return

        self.current_page += 1
        self.apply_filters()

    def browse_file(self):
        if self._is_worker_running():
            return

        file_path, _ = QFileDialog.getOpenFileName(
            self.page,
            "ID 목록 파일 선택",
            "",
            "ID 목록 파일 (*.txt *.csv);;TXT 파일 (*.txt);;CSV 파일 (*.csv)",
        )

        if not file_path:
            return

        self.page.file_path_input.setText(file_path)
        self._select_file_type_by_extension(file_path)

    def import_file(self):
        target_type = self._get_target_type()
        file_type = self._get_file_type()

        if not file_type:
            return

        self._start_import(
            target_type=target_type,
            file_type=file_type,
            import_source="file",
        )

    def import_pixiv_follow(self):
        self._start_pixiv_import("follow")

    def import_pixiv_bookmark(self):
        self._start_pixiv_import("bookmark")

    def cancel_import(self):
        if not self._is_worker_running():
            return

        if self.page.worker is None:
            return

        self.page.worker.request_cancel()
        self.page.cancel_import_button.setEnabled(False)
        self.page.status_label.setText(
            "취소 요청됨: 현재 항목 처리 후 중단합니다."
        )

        self._add_log(
            target="-",
            result="취소 요청",
            message="사용자가 가져오기 취소를 요청했습니다.",
            new_count=0,
            duplicate_in_file_count=0,
            duplicate_existing_count=0,
            error_count=0,
        )

    def clear_logs(self):
        self.page.log_table.clear_logs()
        self.page.status_label.setText("결과 로그를 초기화했습니다.")

    def select_all_displayed(self):
        if self.page.tab_widget.currentIndex() == 0:
            self.page.follow_table.check_all()
            return

        self.page.bookmark_table.check_all()

    def clear_selection(self):
        if self.page.tab_widget.currentIndex() == 0:
            self.page.follow_table.clear_checks()
            return

        self.page.bookmark_table.clear_checks()

    def open_selected_pixiv(self):
        if self.page.tab_widget.currentIndex() == 0:
            self.page.follow_table.open_selected_pixiv()
            return

        self.page.bookmark_table.open_selected_pixiv()

    def delete_selected(self):
        if self._is_worker_running():
            return

        if self.page.tab_widget.currentIndex() == 0:
            ids = self.page.follow_table.get_checked_ids()
            self._delete_follow_users(ids, "선택 삭제")
            return

        ids = self.page.bookmark_table.get_checked_ids()
        self._delete_bookmark_artworks(ids, "선택 삭제")

    def delete_displayed(self):
        if self._is_worker_running():
            return

        if self.page.tab_widget.currentIndex() == 0:
            ids = self.page.follow_table.get_displayed_ids()
            self._delete_follow_users(ids, "현재 페이지 삭제")
            return

        ids = self.page.bookmark_table.get_displayed_ids()
        self._delete_bookmark_artworks(ids, "현재 페이지 삭제")

    def handle_tab_changed(self):
        self.current_page = 1
        self.apply_filters()

    def shutdown_worker(self):
        if self.page.worker_thread is None:
            return

        if self._is_worker_running() and self.page.worker is not None:
            self.page.worker.request_cancel()

        if self.page.worker_thread.isRunning():
            self.page.worker_thread.quit()
            self.page.worker_thread.wait(3000)

        self.page.worker = None
        self.page.worker_thread = None

    def _start_pixiv_import(
        self,
        target_type: str,
    ):
        if self._is_worker_running():
            self.page.status_label.setText(
                "이미 가져오기가 진행 중입니다."
            )
            return

        phpsessid = self.settings_service.get_setting("pixiv_phpsessid")

        if not phpsessid:
            self._add_log(
                target=self._get_target_label(target_type),
                result="세션 오류",
                message="Pixiv PHPSESSID가 설정되어 있지 않습니다.",
                new_count=0,
                duplicate_in_file_count=0,
                duplicate_existing_count=0,
                error_count=1,
            )
            self.page.status_label.setText(
                "Pixiv PHPSESSID가 설정되어 있지 않습니다."
            )
            return

        selected_items = self._get_selected_pixiv_items(target_type)

        if not selected_items:
            self.page.status_label.setText("선택된 항목이 없습니다.")
            self._add_log(
                target=self._get_target_label(target_type),
                result="스킵",
                message="선택된 항목이 없습니다.",
                new_count=0,
                duplicate_in_file_count=0,
                duplicate_existing_count=0,
                error_count=0,
            )
            return

        self._add_log(
            target=self._get_target_label(target_type),
            result="시작",
            message=f"선택 항목 {len(selected_items)}개 메타데이터 갱신 준비 중",
            new_count=0,
            duplicate_in_file_count=0,
            duplicate_existing_count=0,
            error_count=0,
        )

        self._start_import(
            target_type=target_type,
            file_type="pixiv",
            import_source="pixiv",
            phpsessid=phpsessid,
            selected_items=selected_items,
        )

    def _get_selected_pixiv_items(
        self,
        target_type: str,
    ) -> list[dict]:
        if target_type == "follow":
            selected_ids = self.page.follow_table.get_checked_ids()

            if not selected_ids:
                return []

            selected_id_set = set(selected_ids)

            return [
                item
                for item in self.follow_users
                if int(item.get("id", 0) or 0) in selected_id_set
            ]

        selected_ids = self.page.bookmark_table.get_checked_ids()

        if not selected_ids:
            return []

        selected_id_set = set(selected_ids)

        return [
            item
            for item in self.bookmark_artworks
            if int(item.get("id", 0) or 0) in selected_id_set
        ]

    def _get_current_source_items(self) -> tuple[list[dict], str]:
        if self.page.tab_widget.currentIndex() == 0:
            return self.follow_users, "pixiv_user_id"

        return self.bookmark_artworks, "artwork_id"

    def _load_current_table(
        self,
        page_items: list[dict],
    ):
        if self.page.tab_widget.currentIndex() == 0:
            self.page.follow_table.load_follow_users(page_items)
            return

        self.page.bookmark_table.load_bookmark_artworks(page_items)

    def _get_page_size(self) -> int:
        try:
            return int(self.page.page_size_combo.currentText())
        except ValueError:
            return 100

    def _get_max_page(
        self,
        item_count: int,
    ) -> int:
        if item_count <= 0:
            return 1

        return max(1, ceil(item_count / self._get_page_size()))

    def _get_current_page_items(
        self,
        items: list[dict],
    ) -> list[dict]:
        max_page = self._get_max_page(len(items))

        if self.current_page > max_page:
            self.current_page = max_page

        if self.current_page < 1:
            self.current_page = 1

        page_size = self._get_page_size()
        start_index = (self.current_page - 1) * page_size
        end_index = start_index + page_size

        return items[start_index:end_index]

    def _update_page_labels(
        self,
        total_count: int,
        filtered_count: int,
        page_count: int,
    ):
        max_page = self._get_max_page(filtered_count)

        self.page.page_info_label.setText(
            f"페이지: {self.current_page} / {max_page}"
        )
        self.page.display_count_label.setText(
            f"표시: {page_count} / {filtered_count} "
            f"(전체 {total_count})"
        )

        self.page.prev_page_button.setEnabled(self.current_page > 1)
        self.page.next_page_button.setEnabled(self.current_page < max_page)

    def _delete_follow_users(
        self,
        ids: list[int],
        action_label: str,
    ):
        if not ids:
            self.page.status_label.setText("삭제할 팔로우 유저가 없습니다.")
            return

        deleted_count = 0
        error_count = 0

        for follow_user_id in ids:
            try:
                self.follow_service.delete_follow_user(follow_user_id)
                deleted_count += 1
            except Exception:
                error_count += 1

        self._add_log(
            target="팔로우",
            result="완료",
            message=f"{action_label}: {deleted_count}명 삭제",
            new_count=0,
            duplicate_in_file_count=0,
            duplicate_existing_count=0,
            error_count=error_count,
        )

        self.load_data()
        self.page.status_label.setText(
            f"팔로우 유저 {deleted_count}명을 삭제했습니다."
        )

    def _delete_bookmark_artworks(
        self,
        ids: list[int],
        action_label: str,
    ):
        if not ids:
            self.page.status_label.setText("삭제할 북마크 작품이 없습니다.")
            return

        deleted_count = 0
        error_count = 0

        for bookmark_artwork_id in ids:
            try:
                self.bookmark_service.delete_bookmark_artwork(
                    bookmark_artwork_id
                )
                deleted_count += 1
            except Exception:
                error_count += 1

        self._add_log(
            target="북마크",
            result="완료",
            message=f"{action_label}: {deleted_count}개 삭제",
            new_count=0,
            duplicate_in_file_count=0,
            duplicate_existing_count=0,
            error_count=error_count,
        )

        self.load_data()
        self.page.status_label.setText(
            f"북마크 작품 {deleted_count}개를 삭제했습니다."
        )

    def _start_import(
        self,
        target_type: str,
        file_type: str,
        import_source: str = "file",
        phpsessid: str = "",
        selected_items: list[dict] | None = None,
    ):
        if self._is_worker_running():
            self.page.status_label.setText(
                "이미 가져오기가 진행 중입니다."
            )
            return

        file_path = ""

        if import_source == "file":
            file_path = self._get_file_path()

            if not file_path:
                return

        self._set_import_running(True)

        total = len(selected_items or [])

        self.page.progress_bar.setRange(0, max(total, 1))
        self.page.progress_bar.setValue(0)
        self.page.progress_bar.setFormat(f"0 / {total}")
        self.page.estimated_time_label.setText("예상 남은 시간: 계산 중")
        self.page.status_label.setText("가져오기 준비 중...")

        worker_thread = QThread(self.page)
        worker = PixivImportWorker(
            target_type=target_type,
            file_type=file_type,
            file_path=file_path,
            import_source=import_source,
            phpsessid=phpsessid,
            selected_items=selected_items or [],
        )

        self.page.worker_thread = worker_thread
        self.page.worker = worker

        worker.moveToThread(worker_thread)

        worker_thread.started.connect(worker.run)
        worker.progress_updated.connect(self._handle_progress_updated)
        worker.estimated_time_updated.connect(
            self._handle_estimated_time_updated
        )
        worker.log_requested.connect(self._handle_worker_log)
        worker.finished.connect(self._handle_import_finished)
        worker.failed.connect(self._handle_import_failed)

        worker.finished.connect(worker_thread.quit)
        worker.failed.connect(worker_thread.quit)

        worker.finished.connect(worker.deleteLater)
        worker.failed.connect(worker.deleteLater)

        worker_thread.finished.connect(worker_thread.deleteLater)
        worker_thread.finished.connect(self._cleanup_worker)

        worker_thread.start()

    @Slot(int, int, str)
    def _handle_progress_updated(
        self,
        current: int,
        total: int,
        message: str,
    ):
        if total <= 0:
            self.page.progress_bar.setRange(0, 1)
            self.page.progress_bar.setValue(1)
            self.page.progress_bar.setFormat("0 / 0")
        else:
            self.page.progress_bar.setRange(0, total)
            self.page.progress_bar.setValue(current)
            self.page.progress_bar.setFormat(f"{current} / {total}")

        self.page.status_label.setText(message)

    @Slot(str)
    def _handle_estimated_time_updated(
        self,
        text: str,
    ):
        self.page.estimated_time_label.setText(
            f"예상 남은 시간: {text}"
        )

    @Slot(dict)
    def _handle_worker_log(
        self,
        row_data: dict,
    ):
        self._add_log(
            target=row_data.get("target", "-"),
            result=row_data.get("result", "-"),
            message=row_data.get("message", "-"),
            new_count=row_data.get("new_count", 0),
            duplicate_in_file_count=row_data.get(
                "duplicate_in_file_count",
                0,
            ),
            duplicate_existing_count=row_data.get(
                "duplicate_existing_count",
                0,
            ),
            error_count=row_data.get("error_count", 0),
        )

    @Slot(dict)
    def _handle_import_finished(
        self,
        result: dict,
    ):
        target_type = result.get("target_type", "")
        file_type = result.get("file_type", "")
        import_source = result.get("import_source", "file")
        save_result = result.get("save_result", {})
        cancelled = bool(result.get("cancelled", False))

        target_label = self._get_target_label(target_type)

        if import_source == "pixiv":
            self._handle_pixiv_import_finished(
                result=result,
                target_label=target_label,
            )
            return

        log_result = "취소" if cancelled else "저장"

        self._add_log(
            target=target_label,
            result=log_result,
            message=self._format_file_import_finished_message(
                target_label=target_label,
                file_type=file_type,
                result=result,
                save_result=save_result,
                cancelled=cancelled,
            ),
            new_count=result.get("new_count", 0),
            duplicate_in_file_count=result.get(
                "duplicate_in_file_count",
                0,
            ),
            duplicate_existing_count=result.get(
                "duplicate_existing_count",
                0,
            ),
            error_count=save_result.get("error_count", 0),
        )

        self._set_import_running(False)
        self.current_page = 1
        self.load_data()

        self.page.status_label.setText(
            self._format_file_import_finished_message(
                target_label=target_label,
                file_type=file_type,
                result=result,
                save_result=save_result,
                cancelled=cancelled,
            )
        )

    def _handle_pixiv_import_finished(
        self,
        result: dict,
        target_label: str,
    ):
        save_result = result.get("save_result", {})
        sync_result = result.get("sync_result", {})
        is_success = bool(result.get("success"))
        is_cancelled = bool(result.get("cancelled"))
        message = result.get("message", "")

        if is_cancelled:
            log_result = "취소"
        elif is_success:
            log_result = "완료"
        else:
            log_result = self._get_pixiv_error_result_label(
                result.get("reason", "")
            )

        self._add_log(
            target=target_label,
            result=log_result,
            message=message,
            new_count=sync_result.get("success_count", 0),
            duplicate_in_file_count=sync_result.get("skipped_count", 0),
            duplicate_existing_count=0,
            error_count=sync_result.get(
                "error_count",
                save_result.get("error_count", 0),
            ),
        )

        self._add_log(
            target=target_label,
            result="요약",
            message=(
                f"총 {sync_result.get('total_count', 0)}개 / "
                f"처리 {sync_result.get('processed_count', 0)}개 / "
                f"성공 {sync_result.get('success_count', 0)}개 / "
                f"실패 {sync_result.get('failed_count', 0)}개 / "
                f"스킵 {sync_result.get('skipped_count', 0)}개"
            ),
            new_count=sync_result.get("success_count", 0),
            duplicate_in_file_count=sync_result.get("skipped_count", 0),
            duplicate_existing_count=0,
            error_count=sync_result.get(
                "error_count",
                save_result.get("error_count", 0),
            ),
        )

        self._set_import_running(False)
        self.current_page = 1
        self.load_data()
        self.page.status_label.setText(message)

    @Slot(str)
    def _handle_import_failed(
        self,
        message: str,
    ):
        self._set_import_running(False)

        self._add_log(
            target="-",
            result="오류",
            message=message,
            new_count=0,
            duplicate_in_file_count=0,
            duplicate_existing_count=0,
            error_count=1,
        )

        self.page.status_label.setText(f"가져오기 실패: {message}")

    @Slot()
    def _cleanup_worker(self):
        self.page.worker = None
        self.page.worker_thread = None

    def _set_import_running(
        self,
        is_running: bool,
    ):
        self.page.import_file_button.setEnabled(not is_running)
        self.page.browse_file_button.setEnabled(not is_running)
        self.page.import_target_combo.setEnabled(not is_running)
        self.page.import_file_type_combo.setEnabled(not is_running)
        self.page.refresh_button.setEnabled(not is_running)
        self.page.filter_combo.setEnabled(not is_running)
        self.page.page_size_combo.setEnabled(not is_running)
        self.page.tab_widget.setEnabled(not is_running)
        self.page.select_all_button.setEnabled(not is_running)
        self.page.clear_selection_button.setEnabled(not is_running)
        self.page.open_selected_button.setEnabled(not is_running)
        self.page.delete_selected_button.setEnabled(not is_running)
        self.page.delete_displayed_button.setEnabled(not is_running)
        self.page.pixiv_follow_button.setEnabled(not is_running)
        self.page.pixiv_bookmark_button.setEnabled(not is_running)
        self.page.cancel_import_button.setEnabled(is_running)

    def _is_worker_running(self) -> bool:
        return (
            self.page.worker_thread is not None
            and self.page.worker_thread.isRunning()
        )

    def _get_file_path(self) -> str:
        file_path = self.page.file_path_input.text().strip()

        if not file_path:
            self.page.status_label.setText(
                "가져올 파일 경로를 입력하세요."
            )
            return ""

        path = Path(file_path)

        if not path.exists():
            self.page.status_label.setText(
                f"파일을 찾을 수 없습니다: {file_path}"
            )
            return ""

        return str(path)

    def _get_target_type(self) -> str:
        target_text = self.page.import_target_combo.currentText()

        if target_text == "북마크 작품":
            return "bookmark"

        return "follow"

    def _get_file_type(self) -> str:
        file_type_text = self.page.import_file_type_combo.currentText()

        if file_type_text == "TXT":
            return "txt"

        if file_type_text == "CSV":
            return "csv"

        file_path = self.page.file_path_input.text().strip()
        extension = Path(file_path).suffix.lower()

        if extension == ".txt":
            return "txt"

        if extension == ".csv":
            return "csv"

        self.page.status_label.setText(
            "파일 형식을 자동 감지할 수 없습니다. TXT 또는 CSV를 선택하세요."
        )

        return ""

    def _select_file_type_by_extension(
        self,
        file_path: str,
    ):
        extension = Path(file_path).suffix.lower()

        if extension == ".txt":
            self.page.import_file_type_combo.setCurrentText("TXT")
            return

        if extension == ".csv":
            self.page.import_file_type_combo.setCurrentText("CSV")
            return

        self.page.import_file_type_combo.setCurrentText("자동 감지")

    def _filter_items(
        self,
        items: list[dict],
        id_field: str,
    ) -> list[dict]:
        category = self.page.filter_combo.currentText()

        filtered_items = []

        for item in items:
            if not self._match_category(item, category):
                continue

            filtered_items.append(item)

        return filtered_items

    def _match_category(
        self,
        item: dict,
        category: str,
    ) -> bool:
        if category == "전체":
            return True

        if category == "등록":
            return bool(item.get("is_local_artist"))

        sync_status = str(item.get("sync_status", "") or "pending")

        if category == "동기화 필요":
            return (
                not str(item.get("last_synced_at", "") or "").strip()
                or sync_status in {"pending", "failed"}
            )

        if category == "완료":
            return sync_status == "synced"

        if category == "대기":
            return sync_status == "pending"

        if category == "실패":
            return sync_status == "failed"

        if category == "스킵":
            return sync_status == "skipped"

        return True

    def _build_summary(
        self,
        follow_users: list[dict],
        bookmark_artworks: list[dict],
    ) -> dict:
        follow_total = len(follow_users)
        bookmark_total = len(bookmark_artworks)

        follow_matched = sum(
            1
            for item in follow_users
            if item.get("is_local_artist")
        )
        bookmark_matched = sum(
            1
            for item in bookmark_artworks
            if item.get("is_local_artist")
        )

        return {
            "follow_total": follow_total,
            "follow_matched": follow_matched,
            "follow_unmatched": follow_total - follow_matched,
            "bookmark_total": bookmark_total,
            "bookmark_matched": bookmark_matched,
            "bookmark_unmatched": bookmark_total - bookmark_matched,
        }

    def _format_file_import_finished_message(
        self,
        target_label: str,
        file_type: str,
        result: dict,
        save_result: dict,
        cancelled: bool,
    ) -> str:
        action_label = "취소" if cancelled else "완료"

        return (
            f"{target_label} {file_type.upper()} 가져오기 {action_label}: "
            f"신규 {result.get('new_count', 0)}개 / "
            f"저장 {save_result.get('saved_count', 0)}개 / "
            f"오류 {save_result.get('error_count', 0)}개"
        )

    def _add_log(
        self,
        target: str,
        result: str,
        message: str,
        new_count: int,
        duplicate_in_file_count: int,
        duplicate_existing_count: int,
        error_count: int,
    ):
        self.page.log_table.add_log_row(
            {
                "time": datetime.now().strftime("%H:%M:%S"),
                "target": target,
                "result": result,
                "message": message,
                "new_count": new_count,
                "duplicate_in_file_count": duplicate_in_file_count,
                "duplicate_existing_count": duplicate_existing_count,
                "error_count": error_count,
            }
        )

    def _get_target_label(
        self,
        target_type: str,
    ) -> str:
        if target_type == "bookmark":
            return "북마크"

        return "팔로우"

    def _get_pixiv_error_result_label(
        self,
        reason: str,
    ) -> str:
        if reason == "NO_SELECTION":
            return "스킵"

        if reason == "CANCELLED":
            return "취소"

        if reason in (
            "COOKIE_EXPIRED",
            "COOKIE_MISSING",
        ):
            return "세션 오류"

        if reason == "RATE_LIMIT":
            return "요청 제한"

        return "실패"
