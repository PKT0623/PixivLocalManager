from datetime import datetime

from app.services.bookmark import BookmarkService
from app.services.follow import FollowService
from app.services.pixiv.metadata_service import PixivMetadataService
from app.services.pixiv_update_service import PixivRequestError
from app.services.tag import TagService


class PixivSyncStatus:
    PENDING = "pending"
    SYNCED = "synced"
    FAILED = "failed"
    SKIPPED = "skipped"


class PixivSyncService:
    def __init__(
        self,
        metadata_service: PixivMetadataService | None = None,
    ):
        self.metadata_service = metadata_service or PixivMetadataService()
        self.follow_service = FollowService()
        self.bookmark_service = BookmarkService()
        self.tag_service = TagService()

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
                self._update_follow_sync_result(
                    follow_user_id,
                    PixivSyncStatus.SKIPPED,
                    "Pixiv 유저 ID가 비어 있습니다.",
                    follow_user.get("sync_retry_count", 0),
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

                retry_count = int(
                    follow_user.get("sync_retry_count", 0) or 0
                ) + 1
                error_message = self._format_error(error)

                self._update_follow_sync_result(
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
                    f"({index}/{total}) {pixiv_user_id} 갱신 실패: {error_message}",
                )

                if consecutive_failures >= max_consecutive_failures:
                    self._emit_log(
                        log_callback,
                        "요청 제한",
                        (
                            f"연속 실패 {consecutive_failures}회 발생. "
                            "작업을 중단합니다."
                        ),
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
            "errors": errors,
        }

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
                self._update_bookmark_sync_result(
                    bookmark_artwork_id,
                    PixivSyncStatus.SKIPPED,
                    "작품 ID가 비어 있습니다.",
                    bookmark_artwork.get("sync_retry_count", 0),
                )
                self._emit_log(
                    log_callback,
                    "스킵",
                    f"({index}/{total}) 작품 ID가 비어 있습니다.",
                )
                continue

            self._emit_progress(
                progress_callback,
                index - 1,
                total,
                f"({index}/{total}) {artwork_id} 요청 준비 중",
            )

            try:
                metadata = self.metadata_service.fetch_artwork_metadata(
                    artwork_id=artwork_id,
                    phpsessid=phpsessid,
                )

                merged_tags = self._merge_pixiv_tags(
                    existing_tags=bookmark_artwork.get("pixiv_tags", ""),
                    new_tags=metadata.pixiv_tags,
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

                retry_count = int(
                    bookmark_artwork.get("sync_retry_count", 0) or 0
                ) + 1
                error_message = self._format_error(error)

                self._update_bookmark_sync_result(
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
                    f"({index}/{total}) {artwork_id} 갱신 실패: {error_message}",
                )

                if consecutive_failures >= max_consecutive_failures:
                    self._emit_log(
                        log_callback,
                        "요청 제한",
                        (
                            f"연속 실패 {consecutive_failures}회 발생. "
                            "작업을 중단합니다."
                        ),
                    )
                    break

            self._emit_progress(
                progress_callback,
                index,
                total,
                f"북마크 메타데이터 갱신 중: {index} / {total}",
            )

        return {
            "total_count": total,
            "processed_count": processed_count,
            "success_count": success_count,
            "failed_count": failed_count,
            "skipped_count": skipped_count,
            "error_count": failed_count,
            "cancelled": cancelled,
            "errors": errors,
        }

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
