class ResultBuilderMixin:
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
