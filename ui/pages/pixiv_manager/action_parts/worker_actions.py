from PySide6.QtCore import QThread, Slot

from ..worker import PixivImportWorker


class PixivManagerWorkerActions:
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

        message = self._format_file_import_finished_message(
            target_label=target_label,
            file_type=file_type,
            result=result,
            save_result=save_result,
            cancelled=cancelled,
        )

        self._add_log(
            target=target_label,
            result=log_result,
            message=message,
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

        self.page.status_label.setText(message)

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
