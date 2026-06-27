from PySide6.QtCore import QThread, Qt, QTimer, Slot

from ..worker import PixivImportWorker


class PixivManagerWorkerActions:
    PIXIV_STATUS_POLL_INTERVAL_MS = 200

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
        self._stop_pixiv_status_poll_timer()

        if import_source == "file" and not file_path:
            file_path = self._get_file_path()

            if not file_path:
                return

        self._set_import_running(True)

        self.page.progress_bar.setRange(0, 100)
        self.page.progress_bar.setValue(0)
        self.page.progress_bar.setFormat("0%")

        if import_source == "pixiv":
            self.page.status_label.setText("Pixiv 동기화 준비 중...")
        else:
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
            Qt.ConnectionType.QueuedConnection,
        )

        worker.progress_updated.connect(
            self._handle_progress_updated,
            Qt.ConnectionType.QueuedConnection,
        )

        worker.finished.connect(
            lambda: self._capture_worker_result(worker),
            Qt.ConnectionType.DirectConnection,
        )
        worker.failed.connect(
            lambda: self._capture_worker_result(worker),
            Qt.ConnectionType.DirectConnection,
        )

        worker.finished.connect(
            worker_thread.quit,
            Qt.ConnectionType.QueuedConnection,
        )
        worker.failed.connect(
            worker_thread.quit,
            Qt.ConnectionType.QueuedConnection,
        )

        worker_thread.finished.connect(
            self._handle_worker_thread_finished,
            Qt.ConnectionType.QueuedConnection,
        )

        worker_thread.start()

        if import_source == "pixiv":
            self._start_pixiv_status_poll_timer()

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
        worker = self.page.worker

        if worker is not None and getattr(worker, "import_source", "") == "pixiv":
            return

        percent = self._calculate_percent(current, total)

        self.page.progress_bar.setRange(0, 100)
        self.page.progress_bar.setValue(percent)

        if total <= 0:
            self.page.progress_bar.setFormat(f"{percent}%")
        else:
            self.page.progress_bar.setFormat(
                f"{percent}% ({current} / {total})"
            )

        if message:
            self.page.status_label.setText(message)

    @Slot()
    def _handle_worker_thread_finished(self):
        self._stop_pixiv_status_poll_timer()

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

        self._process_worker_result(
            result,
            error_message,
        )

        self.page.worker = None
        self.page.worker_thread = None
        self._pending_worker_result = None
        self._pending_worker_error_message = ""

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

        self.page.progress_bar.setRange(0, 100)
        self.page.progress_bar.setValue(100)
        self.page.progress_bar.setFormat("100%")

        self._set_import_running(False)
        self.current_page = 1

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

        self.page.status_label.setText(
            f"{message} 새로고침 버튼을 누르면 목록이 갱신됩니다."
        )

    def _handle_pixiv_import_finished(
        self,
        result: dict,
        target_label: str,
    ):
        sync_result = result.get("sync_result", {})
        message = result.get("message", "")

        processed_count = sync_result.get("processed_count", 0)
        success_count = sync_result.get("success_count", 0)
        failed_count = sync_result.get("failed_count", 0)
        skipped_count = sync_result.get("skipped_count", 0)
        error_count = sync_result.get("error_count", 0)

        self.page.progress_bar.setRange(0, 100)
        self.page.progress_bar.setValue(100)
        self.page.progress_bar.setFormat("100%")

        result_label = "완료"

        if result.get("reason") == "CANCELLED":
            result_label = "취소"
        elif result.get("reason") == "STOPPED":
            result_label = "중단"
        elif not result.get("success"):
            result_label = "오류"

        status_message = (
            f"{message} / "
            f"처리 {processed_count}개, "
            f"성공 {success_count}개, "
            f"실패 {failed_count}개, "
            f"스킵 {skipped_count}개"
        )

        self._set_import_running(False)
        self.current_page = 1

        self._add_log(
            target=target_label,
            result=result_label,
            message=status_message,
            new_count=success_count,
            duplicate_in_file_count=skipped_count,
            duplicate_existing_count=0,
            error_count=error_count,
        )

        self.page.status_label.setText(
            f"{status_message} 새로고침 버튼을 누르면 목록이 갱신됩니다."
        )

    @Slot(str)
    def _handle_import_failed(
        self,
        message: str,
    ):
        self._stop_pixiv_status_poll_timer()
        self._set_import_running(False)

        self._add_log(
            target="-",
            result="오류",
            message=f"가져오기 실패: {message}",
            new_count=0,
            duplicate_in_file_count=0,
            duplicate_existing_count=0,
            error_count=1,
        )

        self.page.status_label.setText(f"가져오기 실패: {message}")

    def _start_pixiv_status_poll_timer(self):
        self._stop_pixiv_status_poll_timer()

        timer = QTimer(self.page)
        timer.setInterval(self.PIXIV_STATUS_POLL_INTERVAL_MS)
        timer.timeout.connect(self._update_pixiv_status_from_worker)

        self.page.pixiv_status_poll_timer = timer
        timer.start()

    def _stop_pixiv_status_poll_timer(self):
        timer = getattr(self.page, "pixiv_status_poll_timer", None)

        if timer is None:
            return

        timer.stop()
        timer.deleteLater()
        self.page.pixiv_status_poll_timer = None

    def _update_pixiv_status_from_worker(self):
        worker = self.page.worker

        if worker is None:
            return

        if getattr(worker, "import_source", "") != "pixiv":
            return

        current = int(getattr(worker, "current_progress", 0) or 0)
        total = int(getattr(worker, "current_total", 0) or 0)
        percent = self._calculate_percent(current, total)

        if total <= 0:
            self.page.status_label.setText("Pixiv 동기화 중...")
            return

        self.page.status_label.setText(
            f"Pixiv 동기화 중: {percent}% ({current} / {total})"
        )

    def _cleanup_finished_worker_refs(self):
        worker_thread = self.page.worker_thread

        if worker_thread is not None and not worker_thread.isRunning():
            self.page.worker = None
            self.page.worker_thread = None

    def shutdown_worker(self):
        self._stop_pixiv_status_poll_timer()

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

    def _calculate_percent(
        self,
        current: int,
        total: int,
    ) -> int:
        if total <= 0:
            return 0

        safe_current = min(max(current, 0), total)
        return int(safe_current * 100 / total)
