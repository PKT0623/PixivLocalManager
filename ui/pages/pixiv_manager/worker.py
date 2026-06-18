import time

from PySide6.QtCore import QObject, Signal, Slot

from app.services import BookmarkService, FollowService, SettingsService
from app.services.pixiv.metadata_service import PixivMetadataService
from app.services.pixiv.sync_service import PixivSyncService
from app.services.pixiv_update_service import (
    PixivRequestReason,
    PixivUpdateService,
)


class PixivImportWorker(QObject):
    progress_updated = Signal(int, int, str)
    estimated_time_updated = Signal(str)
    log_requested = Signal(dict)
    finished = Signal(dict)
    failed = Signal(str)

    def __init__(
        self,
        target_type: str,
        file_type: str = "",
        file_path: str = "",
        import_source: str = "file",
        phpsessid: str = "",
        selected_items: list[dict] | None = None,
    ):
        super().__init__()

        self.target_type = target_type
        self.file_type = file_type
        self.file_path = file_path
        self.import_source = import_source
        self.phpsessid = phpsessid
        self.selected_items = selected_items or []

        self.started_at = 0.0
        self.target_label = self._get_target_label(target_type)

        self.current_progress = 0
        self.current_total = 0
        self.cancel_requested = False

    @Slot()
    def run(self):
        try:
            if self.import_source == "pixiv":
                result = self._import_from_pixiv()
            elif self.target_type == "follow":
                result = self._import_follow()
            else:
                result = self._import_bookmark()

            self.finished.emit(result)
        except Exception as error:
            self.failed.emit(str(error))

    @Slot()
    def request_cancel(self):
        self.cancel_requested = True
        self._handle_rate_limit_status(
            "취소 요청됨: 현재 항목 처리 후 중단합니다."
        )

    def _import_from_pixiv(self) -> dict:
        self.started_at = time.time()

        total = len(self.selected_items)
        self.current_total = total
        self.current_progress = 0

        if total <= 0:
            return self._build_pixiv_result(
                success=False,
                reason="NO_SELECTION",
                message="선택된 항목이 없습니다.",
                sync_result={
                    "total_count": 0,
                    "processed_count": 0,
                    "success_count": 0,
                    "failed_count": 0,
                    "skipped_count": 0,
                    "error_count": 0,
                    "cancelled": False,
                    "errors": [],
                },
            )

        self._emit_direct_progress(
            0,
            total,
            f"Pixiv {self.target_label} 세션 확인 중...",
        )
        self.estimated_time_updated.emit("계산 중")

        settings_service = SettingsService()
        pixiv_update_service = PixivUpdateService.from_settings(
            settings_service
        )
        pixiv_update_service.set_request_callbacks(
            log_callback=self._handle_sync_log,
            status_callback=self._handle_rate_limit_status,
        )

        session_result = pixiv_update_service.test_phpsessid(self.phpsessid)

        if not session_result.get("success"):
            return self._build_pixiv_result(
                success=False,
                reason=session_result.get("reason"),
                message=session_result.get("message"),
                sync_result={
                    "total_count": total,
                    "processed_count": 0,
                    "success_count": 0,
                    "failed_count": 1,
                    "skipped_count": 0,
                    "error_count": 1,
                    "cancelled": False,
                    "errors": [],
                },
            )

        if self.cancel_requested:
            return self._build_cancelled_pixiv_result(
                total=total,
                processed_count=0,
                success_count=0,
                failed_count=0,
                skipped_count=0,
                errors=[],
            )

        metadata_service = PixivMetadataService(
            pixiv_update_service=pixiv_update_service
        )
        sync_service = PixivSyncService(
            metadata_service=metadata_service
        )

        if self.target_type == "follow":
            sync_result = sync_service.sync_follow_users(
                follow_users=self.selected_items,
                phpsessid=self.phpsessid,
                progress_callback=self._handle_sync_progress,
                log_callback=self._handle_sync_log,
                cancel_callback=self._is_cancel_requested,
            )
        else:
            sync_result = sync_service.sync_bookmark_artworks(
                bookmark_artworks=self.selected_items,
                phpsessid=self.phpsessid,
                progress_callback=self._handle_sync_progress,
                log_callback=self._handle_sync_log,
                cancel_callback=self._is_cancel_requested,
            )

        self._emit_direct_progress(
            sync_result.get("processed_count", 0),
            sync_result.get("total_count", 0),
            f"Pixiv {self.target_label} 메타데이터 갱신 완료",
        )
        self.estimated_time_updated.emit("곧 완료")

        if sync_result.get("cancelled"):
            return self._build_pixiv_result(
                success=False,
                reason="CANCELLED",
                message=self._format_cancelled_message(sync_result),
                sync_result=sync_result,
            )

        return self._build_pixiv_result(
            success=sync_result.get("failed_count", 0) == 0,
            reason=None,
            message=self._format_pixiv_sync_message(sync_result),
            sync_result=sync_result,
        )

    def _import_follow(self) -> dict:
        service = FollowService()

        if self.file_type == "txt":
            items = service.importer.parse_txt_file(self.file_path)
        else:
            items = service.importer.parse_csv_file(self.file_path)

        preview = service.preview_follow_users(items)
        new_items = preview["new_items"]

        save_result = self._save_follow_items(
            service=service,
            items=new_items,
        )

        return {
            **preview,
            "import_source": "file",
            "target_type": "follow",
            "file_type": self.file_type,
            "save_result": save_result,
            "cancelled": self.cancel_requested,
        }

    def _import_bookmark(self) -> dict:
        service = BookmarkService()

        if self.file_type == "txt":
            items = service.importer.parse_txt_file(self.file_path)
        else:
            items = service.importer.parse_csv_file(self.file_path)

        preview = service.preview_bookmark_artworks(items)
        new_items = preview["new_items"]

        save_result = self._save_bookmark_items(
            service=service,
            items=new_items,
        )

        return {
            **preview,
            "import_source": "file",
            "target_type": "bookmark",
            "file_type": self.file_type,
            "save_result": save_result,
            "cancelled": self.cancel_requested,
        }

    def _save_follow_items(
        self,
        service: FollowService,
        items: list[dict],
    ) -> dict:
        saved_count = 0
        error_count = 0
        errors = []

        total = len(items)
        started_at = time.time()

        if total == 0:
            self._emit_direct_progress(0, 0, "저장할 신규 항목이 없습니다.")
            self.estimated_time_updated.emit("-")
            return self._build_save_result(0, 0, 0, [], False)

        for index, item in enumerate(items, start=1):
            if self.cancel_requested:
                self._emit_direct_progress(
                    index - 1,
                    total,
                    "가져오기를 취소했습니다.",
                )
                break

            try:
                service.upsert_follow_user(item)
                saved_count += 1
            except Exception as error:
                error_count += 1
                errors.append(
                    {
                        "pixiv_user_id": item.get("pixiv_user_id", ""),
                        "error": str(error),
                    }
                )

            self._emit_progress(
                index=index,
                total=total,
                started_at=started_at,
            )

        return self._build_save_result(
            total=total,
            saved_count=saved_count,
            error_count=error_count,
            errors=errors,
            cancelled=self.cancel_requested,
        )

    def _save_bookmark_items(
        self,
        service: BookmarkService,
        items: list[dict],
    ) -> dict:
        saved_count = 0
        error_count = 0
        errors = []

        total = len(items)
        started_at = time.time()

        if total == 0:
            self._emit_direct_progress(0, 0, "저장할 신규 항목이 없습니다.")
            self.estimated_time_updated.emit("-")
            return self._build_save_result(0, 0, 0, [], False)

        for index, item in enumerate(items, start=1):
            if self.cancel_requested:
                self._emit_direct_progress(
                    index - 1,
                    total,
                    "가져오기를 취소했습니다.",
                )
                break

            try:
                service.upsert_bookmark_artwork(item)
                saved_count += 1
            except Exception as error:
                error_count += 1
                errors.append(
                    {
                        "artwork_id": item.get("artwork_id", ""),
                        "error": str(error),
                    }
                )

            self._emit_progress(
                index=index,
                total=total,
                started_at=started_at,
            )

        return self._build_save_result(
            total=total,
            saved_count=saved_count,
            error_count=error_count,
            errors=errors,
            cancelled=self.cancel_requested,
        )

    def _handle_sync_progress(
        self,
        current: int,
        total: int,
        message: str,
    ):
        self._emit_direct_progress(current, total, message)

        elapsed = max(time.time() - self.started_at, 0.001)
        average = elapsed / max(current, 1)
        remain = max(total - current, 0)
        remain_seconds = int(average * remain)

        self.estimated_time_updated.emit(
            self._format_seconds(remain_seconds)
        )

    def _handle_rate_limit_status(
        self,
        message: str,
    ):
        self.progress_updated.emit(
            self.current_progress,
            self.current_total,
            message,
        )

    def _handle_sync_log(
        self,
        result: str,
        message: str,
    ):
        self.log_requested.emit(
            {
                "target": self.target_label,
                "result": result,
                "message": message,
                "new_count": 0,
                "duplicate_in_file_count": 0,
                "duplicate_existing_count": 0,
                "error_count": (
                    1
                    if result in ("실패", "세션 오류", "요청 제한")
                    else 0
                ),
            }
        )

    def _emit_direct_progress(
        self,
        current: int,
        total: int,
        message: str,
    ):
        self.current_progress = current
        self.current_total = total
        self.progress_updated.emit(current, total, message)

    def _emit_progress(
        self,
        index: int,
        total: int,
        started_at: float,
    ):
        self._emit_direct_progress(
            index,
            total,
            f"{index} / {total}",
        )

        elapsed = max(time.time() - started_at, 0.001)
        average = elapsed / index
        remain = max(total - index, 0)
        remain_seconds = int(average * remain)

        self.estimated_time_updated.emit(
            self._format_seconds(remain_seconds)
        )

    def _is_cancel_requested(self) -> bool:
        return self.cancel_requested

    def _format_seconds(
        self,
        seconds: int,
    ) -> str:
        if seconds <= 0:
            return "곧 완료"

        minutes = seconds // 60
        remain_seconds = seconds % 60

        if minutes <= 0:
            return f"약 {remain_seconds}초"

        return f"약 {minutes}분 {remain_seconds}초"

    def _format_pixiv_sync_message(
        self,
        result: dict,
    ) -> str:
        return (
            f"Pixiv {self.target_label} 메타데이터 갱신 완료: "
            f"성공 {result.get('success_count', 0)}개, "
            f"실패 {result.get('failed_count', 0)}개, "
            f"스킵 {result.get('skipped_count', 0)}개"
        )

    def _format_cancelled_message(
        self,
        result: dict,
    ) -> str:
        return (
            f"Pixiv {self.target_label} 메타데이터 갱신 취소: "
            f"처리 {result.get('processed_count', 0)}개 / "
            f"성공 {result.get('success_count', 0)}개 / "
            f"실패 {result.get('failed_count', 0)}개 / "
            f"스킵 {result.get('skipped_count', 0)}개"
        )

    def _build_cancelled_pixiv_result(
        self,
        total: int,
        processed_count: int,
        success_count: int,
        failed_count: int,
        skipped_count: int,
        errors: list[dict],
    ) -> dict:
        sync_result = {
            "total_count": total,
            "processed_count": processed_count,
            "success_count": success_count,
            "failed_count": failed_count,
            "skipped_count": skipped_count,
            "error_count": failed_count,
            "cancelled": True,
            "errors": errors,
        }

        return self._build_pixiv_result(
            success=False,
            reason="CANCELLED",
            message=self._format_cancelled_message(sync_result),
            sync_result=sync_result,
        )

    def _build_pixiv_result(
        self,
        success: bool,
        reason,
        message: str,
        sync_result: dict,
    ) -> dict:
        return {
            "import_source": "pixiv",
            "target_type": self.target_type,
            "file_type": "pixiv",
            "success": success,
            "reason": reason,
            "message": message,
            "cancelled": bool(sync_result.get("cancelled", False)),
            "new_count": 0,
            "duplicate_in_file_count": 0,
            "duplicate_existing_count": 0,
            "save_result": self._build_save_result(
                total=sync_result.get("total_count", 0),
                saved_count=sync_result.get("success_count", 0),
                error_count=sync_result.get("error_count", 0),
                errors=sync_result.get("errors", []),
                cancelled=bool(sync_result.get("cancelled", False)),
            ),
            "sync_result": sync_result,
        }

    def _build_save_result(
        self,
        total: int,
        saved_count: int,
        error_count: int,
        errors: list[dict],
        cancelled: bool = False,
    ) -> dict:
        return {
            "total_count": total,
            "saved_count": saved_count,
            "updated_count": 0,
            "skipped_count": 0,
            "error_count": error_count,
            "cancelled": cancelled,
            "errors": errors,
        }

    def get_error_result_label(
        self,
        reason: str,
    ) -> str:
        if reason == PixivRequestReason.COOKIE_EXPIRED:
            return "세션 오류"

        if reason == PixivRequestReason.COOKIE_MISSING:
            return "세션 오류"

        if reason == PixivRequestReason.RATE_LIMIT:
            return "요청 제한"

        return "실패"

    def _get_target_label(
        self,
        target_type: str,
    ) -> str:
        if target_type == "bookmark":
            return "북마크"

        return "팔로우"
