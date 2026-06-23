from .errors import (
    REQUEST_REASON_LABELS,
    PixivRequestError,
    PixivRequestReason,
)
from .models import PixivArtworkFetchResult
from .request_client import PixivUpdateRequestClient
from .response_parser import PixivUpdateResponseParser


class PixivUpdateService:
    PIXIV_PROFILE_ALL_URL = (
        "https://www.pixiv.net/ajax/user/{pixiv_id}/profile/all"
    )
    PIXIV_ACCOUNT_URL = "https://www.pixiv.net/ajax/user/extra"

    DEFAULT_REQUEST_INTERVAL_MS = 2000
    DEFAULT_BATCH_SIZE = 1000
    DEFAULT_BATCH_REST_MS = 300000
    DEFAULT_RETRY_COUNT = 3

    def __init__(
        self,
        request_interval_ms: int | None = None,
        batch_size: int | None = None,
        batch_rest_ms: int | None = None,
        retry_count: int | None = None,
    ):
        self.request_interval_ms = (
            request_interval_ms
            if request_interval_ms is not None
            else self.DEFAULT_REQUEST_INTERVAL_MS
        )
        self.batch_size = (
            batch_size
            if batch_size is not None
            else self.DEFAULT_BATCH_SIZE
        )
        self.batch_rest_ms = (
            batch_rest_ms
            if batch_rest_ms is not None
            else self.DEFAULT_BATCH_REST_MS
        )
        self.retry_count = (
            retry_count
            if retry_count is not None
            else self.DEFAULT_RETRY_COUNT
        )

        self._normalize_request_settings()

        self.request_client = PixivUpdateRequestClient(
            request_interval_ms=self.request_interval_ms,
            batch_size=self.batch_size,
            batch_rest_ms=self.batch_rest_ms,
            retry_count=self.retry_count,
        )
        self.response_parser = PixivUpdateResponseParser()

    @classmethod
    def from_settings(cls, settings_service):
        request_interval_ms = cls._get_request_interval_ms_from_settings(
            settings_service
        )
        batch_size = settings_service.get_int_setting(
            "pixiv_batch_size",
            cls.DEFAULT_BATCH_SIZE,
        )
        batch_rest_ms = settings_service.get_int_setting(
            "pixiv_batch_rest_ms",
            cls.DEFAULT_BATCH_REST_MS,
        )
        retry_count = settings_service.get_int_setting(
            "pixiv_retry_count",
            cls.DEFAULT_RETRY_COUNT,
        )

        return cls(
            request_interval_ms=request_interval_ms,
            batch_size=batch_size,
            batch_rest_ms=batch_rest_ms,
            retry_count=retry_count,
        )

    @classmethod
    def _get_request_interval_ms_from_settings(
        cls,
        settings_service,
    ) -> int:
        new_value = settings_service.get_setting(
            "pixiv_request_interval_ms"
        )

        if new_value not in (None, ""):
            try:
                return int(new_value)
            except (TypeError, ValueError):
                return cls.DEFAULT_REQUEST_INTERVAL_MS

        legacy_min_seconds = settings_service.get_setting(
            "pixiv_request_interval_min"
        )

        if legacy_min_seconds not in (None, ""):
            try:
                return int(legacy_min_seconds) * 1000
            except (TypeError, ValueError):
                return cls.DEFAULT_REQUEST_INTERVAL_MS

        return cls.DEFAULT_REQUEST_INTERVAL_MS

    def set_request_callbacks(
        self,
        log_callback=None,
        status_callback=None,
    ):
        self.request_client.set_request_callbacks(
            log_callback=log_callback,
            status_callback=status_callback,
        )

    def fetch_artist_artwork_ids(
        self,
        pixiv_id: str,
        phpsessid: str,
    ) -> PixivArtworkFetchResult:
        pixiv_id = str(pixiv_id or "").strip()
        phpsessid = str(phpsessid or "").strip()

        if not pixiv_id:
            raise ValueError("Pixiv ID가 없습니다.")

        if not phpsessid:
            raise PixivRequestError(
                reason=PixivRequestReason.COOKIE_MISSING,
                message="Pixiv PHPSESSID가 설정되어 있지 않습니다.",
                should_stop=True,
                retryable=False,
            )

        response_data = self._request_with_retry(
            url=self.PIXIV_PROFILE_ALL_URL.format(
                pixiv_id=pixiv_id,
            ),
            phpsessid=phpsessid,
            referer=f"https://www.pixiv.net/users/{pixiv_id}",
        )

        artwork_ids = self._extract_artwork_ids(response_data)
        artwork_ids = self._sort_artwork_ids(artwork_ids)

        return PixivArtworkFetchResult(
            pixiv_id=pixiv_id,
            artwork_ids=artwork_ids,
            artwork_ids_text=",".join(artwork_ids),
        )

    def test_phpsessid(
        self,
        phpsessid: str,
    ) -> dict:
        phpsessid = str(phpsessid or "").strip()

        if not phpsessid:
            return {
                "success": False,
                "reason": PixivRequestReason.COOKIE_MISSING,
                "message": "PHPSESSID가 비어 있습니다.",
            }

        try:
            response_data = self._request_with_retry(
                url=self.PIXIV_ACCOUNT_URL,
                phpsessid=phpsessid,
                referer="https://www.pixiv.net/",
                wait_before_request=False,
            )
        except PixivRequestError as error:
            return {
                "success": False,
                "reason": error.reason,
                "message": error.to_display_text(),
            }
        except Exception as error:
            return {
                "success": False,
                "reason": PixivRequestReason.UNKNOWN_ERROR,
                "message": str(error),
            }

        if response_data.get("error"):
            message = response_data.get("message") or "Pixiv 오류"
            reason = self._classify_pixiv_error_message(message)

            return {
                "success": False,
                "reason": reason,
                "message": f"[{REQUEST_REASON_LABELS[reason]}] {message}",
            }

        return {
            "success": True,
            "reason": None,
            "message": "PHPSESSID가 정상 동작합니다.",
        }

    def _normalize_request_settings(self):
        self.request_interval_ms = max(
            2000,
            int(self.request_interval_ms),
        )
        self.batch_size = max(
            1,
            int(self.batch_size),
        )
        self.batch_rest_ms = max(
            0,
            int(self.batch_rest_ms),
        )
        self.retry_count = max(
            0,
            int(self.retry_count),
        )

    def _request_with_retry(
        self,
        url: str,
        phpsessid: str,
        referer: str,
        wait_before_request: bool = True,
    ) -> dict:
        return self.request_client.request_with_retry(
            url=url,
            phpsessid=phpsessid,
            referer=referer,
            wait_before_request=wait_before_request,
        )

    def _request_json(
        self,
        url: str,
        phpsessid: str,
        referer: str,
        wait_before_request: bool = True,
    ) -> dict:
        return self.request_client.request_json(
            url=url,
            phpsessid=phpsessid,
            referer=referer,
            wait_before_request=wait_before_request,
        )

    def _extract_artwork_ids(
        self,
        response_data: dict,
    ) -> list[str]:
        return self.response_parser.extract_artwork_ids(response_data)

    def _classify_pixiv_error_message(
        self,
        message: str,
    ) -> str:
        return self.response_parser.classify_pixiv_error_message(message)

    def _extract_ids_from_dict(
        self,
        value,
    ) -> list[str]:
        return self.response_parser.extract_ids_from_dict(value)

    def _sort_artwork_ids(
        self,
        artwork_ids: list[str],
    ) -> list[str]:
        return self.response_parser.sort_artwork_ids(artwork_ids)

    def _sort_key(
        self,
        value: str,
    ):
        return self.response_parser.sort_key(value)
