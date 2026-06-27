import time

from app.services.pixiv_update_service import PixivRequestError

from .constants import PixivSyncStatus


class BookmarkSyncMixin:
    UI_YIELD_SECONDS = 0.001

    def sync_bookmark_artworks(
        self,
        bookmark_artworks: list[dict],
        phpsessid: str,
        progress_callback=None,
        log_callback=None,
        cancel_callback=None,
        max_consecutive_failures: int = 10,
    ) -> dict:
        total = len(bookmark_artworks)
        success_count = 0
        failed_count = 0
        skipped_count = 0
        consecutive_failures = 0
        processed_count = 0
        errors = []
        cancelled = False
        stopped = False
        stop_reason = ""

        for index, bookmark_artwork in enumerate(
            bookmark_artworks,
            start=1,
        ):
            if self._is_cancel_requested(cancel_callback):
                cancelled = True
                self._emit_log(
                    log_callback,
                    "취소",
                    (
                        f"취소 요청으로 북마크 메타데이터 갱신 중단: "
                        f"{processed_count} / {total}"
                    ),
                )
                break

            processed_count = index
            bookmark_artwork_id = bookmark_artwork.get("id")
            artwork_id = str(
                bookmark_artwork.get("artwork_id", "") or ""
            ).strip()

            if not artwork_id:
                skipped_count += 1
                self._safe_update_bookmark_sync_result(
                    bookmark_artwork_id,
                    PixivSyncStatus.SKIPPED,
                    "작품 ID가 비어 있습니다.",
                    self._safe_retry_count(
                        bookmark_artwork.get("sync_retry_count", 0)
                    ),
                )
                self._emit_log(
                    log_callback,
                    "스킵",
                    f"({index}/{total}) 작품 ID가 비어 있습니다.",
                )
                self._emit_progress(
                    progress_callback,
                    index,
                    total,
                    f"북마크 메타데이터 갱신 중: {index} / {total}",
                )
                self._yield_for_ui()
                continue

            self._emit_progress(
                progress_callback,
                index - 1,
                total,
                f"({index}/{total}) {artwork_id} 요청 준비 중",
            )
            self._yield_for_ui()

            try:
                metadata = self.metadata_service.fetch_artwork_metadata(
                    artwork_id=artwork_id,
                    phpsessid=phpsessid,
                )

                merged_tags = self._merge_pixiv_tags(
                    existing_tags=bookmark_artwork.get("pixiv_tags", ""),
                    new_tags=metadata.pixiv_tags,
                    sort_tags=False,
                    prefer_new_order=True,
                )

                update_data = dict(bookmark_artwork)
                update_data.update(
                    {
                        "title": metadata.title,
                        "artist_id": metadata.artist_id,
                        "artist_name": metadata.artist_name,
                        "page_count": metadata.page_count,
                        "ai_type": metadata.ai_type,
                        "is_ai_generated": metadata.is_ai_generated,
                        "pixiv_tags": merged_tags,
                        "last_synced_at": self._now(),
                        "sync_status": PixivSyncStatus.SYNCED,
                        "sync_error_message": "",
                        "sync_retry_count": 0,
                    }
                )

                self.bookmark_service.update_bookmark_artwork(
                    bookmark_artwork_id,
                    update_data,
                    match_local_artist=True,
                )

                success_count += 1
                consecutive_failures = 0

                self._emit_log(
                    log_callback,
                    "성공",
                    f"({index}/{total}) {artwork_id} 메타데이터 갱신 완료",
                )
            except Exception as error:
                failed_count += 1
                consecutive_failures += 1

                retry_count = (
                    self._safe_retry_count(
                        bookmark_artwork.get("sync_retry_count", 0)
                    )
                    + 1
                )
                error_message = self._format_error(error)

                self._safe_update_bookmark_sync_result(
                    bookmark_artwork_id,
                    PixivSyncStatus.FAILED,
                    error_message,
                    retry_count,
                )

                errors.append(
                    {
                        "artwork_id": artwork_id,
                        "error": error_message,
                    }
                )

                self._emit_log(
                    log_callback,
                    self._get_error_log_result(error),
                    (
                        f"({index}/{total}) {artwork_id} "
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
                f"북마크 메타데이터 갱신 중: {index} / {total}",
            )
            self._yield_for_ui()

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

    def _safe_update_bookmark_sync_result(
        self,
        bookmark_artwork_id,
        sync_status: str,
        error_message: str,
        retry_count: int,
    ):
        try:
            self._update_bookmark_sync_result(
                bookmark_artwork_id=bookmark_artwork_id,
                sync_status=sync_status,
                error_message=error_message,
                retry_count=retry_count,
            )
        except Exception:
            return

    def _update_bookmark_sync_result(
        self,
        bookmark_artwork_id,
        sync_status: str,
        error_message: str,
        retry_count: int,
    ):
        if bookmark_artwork_id is None:
            return

        self.bookmark_service.repo.update_sync_result(
            bookmark_artwork_id=int(bookmark_artwork_id),
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

    def _yield_for_ui(self):
        time.sleep(self.UI_YIELD_SECONDS)
