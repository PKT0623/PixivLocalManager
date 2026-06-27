from datetime import datetime

from app.services.pixiv_update_service import (
    PixivRequestError,
    PixivRequestReason,
)


class PixivSyncHelperMixin:
    STOP_REASONS = {
        PixivRequestReason.COOKIE_EXPIRED,
        PixivRequestReason.COOKIE_MISSING,
        PixivRequestReason.RATE_LIMIT,
    }

    def _merge_pixiv_tags(
        self,
        existing_tags,
        new_tags,
        sort_tags: bool = True,
        prefer_new_order: bool = False,
    ) -> str:
        merged_tags = self.tag_service.merge_tags(
            existing_tags=existing_tags,
            new_tags=new_tags,
            sort_tags=sort_tags,
            prefer_new_order=prefer_new_order,
        )

        return self.tag_service.serialize_tags(
            merged_tags,
            sort_tags=sort_tags,
        )

    def _emit_progress(
        self,
        progress_callback,
        current: int,
        total: int,
        message: str,
    ):
        if progress_callback is None:
            return

        progress_callback(
            current,
            total,
            message,
        )

    def _emit_log(
        self,
        log_callback,
        result: str,
        message: str,
    ):
        if log_callback is None:
            return

        log_callback(
            result,
            message,
        )

    def _is_cancel_requested(
        self,
        cancel_callback,
    ) -> bool:
        if cancel_callback is None:
            return False

        try:
            return bool(cancel_callback())
        except Exception:
            return False

    def _format_error(
        self,
        error: Exception,
    ) -> str:
        if isinstance(error, PixivRequestError):
            return error.to_display_text()

        message = str(error).strip()

        if message:
            return message

        return error.__class__.__name__

    def _get_error_log_result(
        self,
        error: Exception,
    ) -> str:
        if not isinstance(error, PixivRequestError):
            return "실패"

        if error.reason in (
            PixivRequestReason.COOKIE_EXPIRED,
            PixivRequestReason.COOKIE_MISSING,
        ):
            return "세션 오류"

        if error.reason == PixivRequestReason.RATE_LIMIT:
            return "요청 제한"

        return "실패"

    def _should_stop_on_error(
        self,
        error: Exception,
    ) -> bool:
        if not isinstance(error, PixivRequestError):
            return False

        if error.should_stop:
            return True

        return error.reason in self.STOP_REASONS

    def _safe_retry_count(
        self,
        value,
    ) -> int:
        try:
            return max(0, int(value or 0))
        except (TypeError, ValueError):
            return 0

    def _now(self) -> str:
        return datetime.now().isoformat()
