import time

from app.services import SettingsService
from app.services.pixiv.metadata_service import PixivMetadataService
from app.services.pixiv.sync_service import PixivSyncService
from app.services.pixiv_update_service import (
    PixivRequestReason,
    PixivUpdateService,
)


class PixivSyncMixin:
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
