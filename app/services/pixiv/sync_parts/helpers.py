from datetime import datetime

from app.services.pixiv_update_service import PixivRequestError


class PixivSyncHelperMixin:
    def _merge_pixiv_tags(
        self,
        existing_tags,
        new_tags,
    ) -> str:
        merged_tags = self.tag_service.merge_tags(
            existing_tags=existing_tags,
            new_tags=new_tags,
        )

        return self.tag_service.serialize_tags(merged_tags)

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

        return str(error)

    def _get_error_log_result(
        self,
        error: Exception,
    ) -> str:
        if not isinstance(error, PixivRequestError):
            return "실패"

        if error.reason in (
            "COOKIE_EXPIRED",
            "COOKIE_MISSING",
        ):
            return "세션 오류"

        if error.reason == "RATE_LIMIT":
            return "요청 제한"

        return "실패"

    def _now(self) -> str:
        return datetime.now().isoformat()
