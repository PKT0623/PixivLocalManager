from PySide6.QtCore import Slot


class PixivManagerWorkerResultActionsMixin:
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
