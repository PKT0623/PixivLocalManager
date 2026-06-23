from app.services.pixiv_update_service import PixivRequestError

from .constants import PixivSyncStatus


class FollowSyncMixin:
    def sync_follow_users(
        self,
        follow_users: list[dict],
        phpsessid: str,
        progress_callback=None,
        log_callback=None,
        cancel_callback=None,
        max_consecutive_failures: int = 10,
    ) -> dict:
        total = len(follow_users)
        success_count = 0
        failed_count = 0
        skipped_count = 0
        consecutive_failures = 0
        processed_count = 0
        errors = []
        cancelled = False
        stopped = False
        stop_reason = ""

        for index, follow_user in enumerate(follow_users, start=1):
            if self._is_cancel_requested(cancel_callback):
                cancelled = True
                self._emit_log(
                    log_callback,
                    "취소",
                    (
                        f"취소 요청으로 팔로우 메타데이터 갱신 중단: "
                        f"{processed_count} / {total}"
                    ),
                )
                break

            processed_count = index
            follow_user_id = follow_user.get("id")
            pixiv_user_id = str(
                follow_user.get("pixiv_user_id", "") or ""
            ).strip()

            if not pixiv_user_id:
                skipped_count += 1
                self._safe_update_follow_sync_result(
                    follow_user_id,
                    PixivSyncStatus.SKIPPED,
                    "Pixiv 유저 ID가 비어 있습니다.",
                    self._safe_retry_count(
                        follow_user.get("sync_retry_count", 0)
                    ),
                )
                self._emit_log(
                    log_callback,
                    "스킵",
                    f"({index}/{total}) Pixiv 유저 ID가 비어 있습니다.",
                )
                continue

            self._emit_progress(
                progress_callback,
                index - 1,
                total,
                f"({index}/{total}) {pixiv_user_id} 요청 준비 중",
            )

            try:
                metadata = self.metadata_service.fetch_user_metadata(
                    pixiv_user_id=pixiv_user_id,
                    phpsessid=phpsessid,
                )

                merged_tags = self._merge_pixiv_tags(
                    existing_tags=follow_user.get("pixiv_tags", ""),
                    new_tags=metadata.pixiv_tags,
                )

                update_data = dict(follow_user)
                update_data.update(
                    {
                        "user_name": metadata.user_name,
                        "artwork_count": metadata.artwork_count,
                        "pixiv_tags": merged_tags,
                        "last_synced_at": self._now(),
                        "sync_status": PixivSyncStatus.SYNCED,
                        "sync_error_message": "",
                        "sync_retry_count": 0,
                    }
                )

                self.follow_service.update_follow_user(
                    follow_user_id,
                    update_data,
                    match_local_artist=True,
                )

                success_count += 1
                consecutive_failures = 0

                self._emit_log(
                    log_callback,
                    "성공",
                    f"({index}/{total}) {pixiv_user_id} 메타데이터 갱신 완료",
                )
            except Exception as error:
                failed_count += 1
                consecutive_failures += 1

                retry_count = (
                    self._safe_retry_count(
                        follow_user.get("sync_retry_count", 0)
                    )
                    + 1
                )
                error_message = self._format_error(error)

                self._safe_update_follow_sync_result(
                    follow_user_id,
                    PixivSyncStatus.FAILED,
                    error_message,
                    retry_count,
                )

                errors.append(
                    {
                        "pixiv_user_id": pixiv_user_id,
                        "error": error_message,
                    }
                )

                self._emit_log(
                    log_callback,
                    self._get_error_log_result(error),
                    (
                        f"({index}/{total}) {pixiv_user_id} "
                        f"갱신 실패: {error_message}"
                    ),
                )

                if self._should_stop_on_error(error):
                    stopped = True
                    stop_reason = self._format_stop_reason(error)
                    self._emit_log(
                        log_callback,
                        self._get_error_log_result(error),
                        f"{stop_reason} 작업을 중단합니다.",
                    )
                    break

                if consecutive_failures >= max_consecutive_failures:
                    stopped = True
                    stop_reason = (
                        f"연속 실패 {consecutive_failures}회 발생."
                    )
                    self._emit_log(
                        log_callback,
                        "요청 제한",
                        f"{stop_reason} 작업을 중단합니다.",
                    )
                    break

            self._emit_progress(
                progress_callback,
                index,
                total,
                f"팔로우 메타데이터 갱신 중: {index} / {total}",
            )

        return {
            "total_count": total,
            "processed_count": processed_count,
            "success_count": success_count,
            "failed_count": failed_count,
            "skipped_count": skipped_count,
            "error_count": failed_count,
            "cancelled": cancelled,
            "stopped": stopped,
            "stop_reason": stop_reason,
            "errors": errors,
        }

    def _safe_update_follow_sync_result(
        self,
        follow_user_id,
        sync_status: str,
        error_message: str,
        retry_count: int,
    ):
        try:
            self._update_follow_sync_result(
                follow_user_id=follow_user_id,
                sync_status=sync_status,
                error_message=error_message,
                retry_count=retry_count,
            )
        except Exception:
            return

    def _update_follow_sync_result(
        self,
        follow_user_id,
        sync_status: str,
        error_message: str,
        retry_count: int,
    ):
        if follow_user_id is None:
            return

        self.follow_service.repo.update_sync_result(
            follow_user_id=int(follow_user_id),
            sync_status=sync_status,
            error_message=error_message,
            retry_count=retry_count,
        )

    def _format_stop_reason(
        self,
        error: Exception,
    ) -> str:
        if isinstance(error, PixivRequestError):
            return error.to_display_text()

        return self._format_error(error)
