from PySide6.QtCore import QThread, Qt, QTimer, Slot

from ..worker import PixivImportWorker


class PixivManagerWorkerActions:
    RELOAD_DELAY_MS = 300

    def _start_import(
        self,
        target_type: str,
        file_type: str,
        import_source: str = "file",
        file_path: str = "",
        phpsessid: str = "",
        selected_items: list[dict] | None = None,
    ):
        if self._is_worker_running():
            self.page.status_label.setText(
                "이미 가져오기가 진행 중입니다."
            )
            return

        self._cleanup_finished_worker_refs()

        if import_source == "file" and not file_path:
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

        self._pending_worker_result = None
        self._pending_worker_error_message = ""

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

        worker_thread.started.connect(
            worker.run,
            Qt.QueuedConnection,
        )

        worker.progress_updated.connect(
            self._handle_progress_updated,
            Qt.QueuedConnection,
        )
        worker.estimated_time_updated.connect(
            self._handle_estimated_time_updated,
            Qt.QueuedConnection,
        )
        worker.log_requested.connect(
            self._handle_worker_log,
            Qt.QueuedConnection,
        )

        worker.finished.connect(
            lambda: self._capture_worker_result(worker),
            Qt.DirectConnection,
        )
        worker.failed.connect(
            lambda: self._capture_worker_result(worker),
            Qt.DirectConnection,
        )

        worker.finished.connect(
            worker.deleteLater,
            Qt.DirectConnection,
        )
        worker.failed.connect(
            worker.deleteLater,
            Qt.DirectConnection,
        )

        worker.finished.connect(
            worker_thread.quit,
            Qt.QueuedConnection,
        )
        worker.failed.connect(
            worker_thread.quit,
            Qt.QueuedConnection,
        )

        worker_thread.finished.connect(
            self._handle_worker_thread_finished,
            Qt.QueuedConnection,
        )
        worker_thread.finished.connect(
            worker_thread.deleteLater,
            Qt.QueuedConnection,
        )

        worker_thread.start()

    def _capture_worker_result(
        self,
        worker,
    ):
        self._pending_worker_result = getattr(
            worker,
            "result_payload",
            None,
        )
        self._pending_worker_error_message = getattr(
            worker,
            "error_message",
            "",
        )

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

    @Slot(object)
    def _handle_worker_log(
        self,
        row_data,
    ):
        if not isinstance(row_data, dict):
            return

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

    @Slot()
    def _handle_worker_thread_finished(self):
        result = getattr(
            self,
            "_pending_worker_result",
            None,
        )
        error_message = getattr(
            self,
            "_pending_worker_error_message",
            "",
        )

        self.page.worker = None
        self.page.worker_thread = None

        QTimer.singleShot(
            0,
            lambda: self._process_worker_result(
                result,
                error_message,
            ),
        )

    def _process_worker_result(
        self,
        result,
        error_message: str,
    ):
        if result is None:
            self._handle_import_failed(
                error_message or "가져오기 결과를 확인하지 못했습니다."
            )
            return

        self._handle_import_finished(result)

    def _handle_import_finished(
        self,
        result: dict,
    ):
        if not isinstance(result, dict):
            self._handle_import_failed("가져오기 결과 형식이 올바르지 않습니다.")
            return

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
        self._reload_data_later(message)

    def _handle_pixiv_import_finished(
        self,
        result: dict,
        target_label: str,
    ):
        sync_result = result.get("sync_result", {})
        message = result.get("message", "")

        total_count = sync_result.get("total_count", 0)
        processed_count = sync_result.get("processed_count", 0)
        success_count = sync_result.get("success_count", 0)
        failed_count = sync_result.get("failed_count", 0)
        skipped_count = sync_result.get("skipped_count", 0)
        error_count = sync_result.get("error_count", 0)

        self._set_import_running(False)

        self.page.progress_bar.setRange(0, max(total_count, 1))
        self.page.progress_bar.setValue(processed_count)
        self.page.progress_bar.setFormat(
            f"{processed_count} / {total_count}"
        )
        self.page.estimated_time_label.setText("예상 남은 시간: 완료")

        result_label = "완료"

        if result.get("reason") == "CANCELLED":
            result_label = "취소"
        elif result.get("reason") == "STOPPED":
            result_label = "중단"
        elif not result.get("success"):
            result_label = "오류"

        self._add_log(
            target=target_label,
            result=result_label,
            message=message,
            new_count=success_count,
            duplicate_in_file_count=skipped_count,
            duplicate_existing_count=0,
            error_count=error_count,
        )

        status_message = (
            f"{message} / "
            f"성공 {success_count}개, "
            f"실패 {failed_count}개, "
            f"스킵 {skipped_count}개 "
        )

        self.current_page = 1
        self._reload_data_later(status_message)

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

    def _reload_data_later(
        self,
        message: str,
    ):
        self.page.status_label.setText(message)

        QTimer.singleShot(
            self.RELOAD_DELAY_MS,
            lambda: self._reload_data_safely(message),
        )

    def _reload_data_safely(
        self,
        message: str,
    ):
        self.page.setUpdatesEnabled(False)

        try:
            self.load_data()
        finally:
            self.page.setUpdatesEnabled(True)
            self.page.status_label.setText(message)
            self.page.update()

    def _cleanup_finished_worker_refs(self):
        if self.page.worker_thread is not None:
            if not self.page.worker_thread.isRunning():
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
        self.page.cancel_import_button.setEnabled(is_running)

        if hasattr(self.page, "pixiv_follow_button"):
            self.page.pixiv_follow_button.setEnabled(not is_running)

        if hasattr(self.page, "pixiv_bookmark_button"):
            self.page.pixiv_bookmark_button.setEnabled(not is_running)

    def _is_worker_running(self) -> bool:
        return (
            self.page.worker_thread is not None
            and self.page.worker_thread.isRunning()
        )
