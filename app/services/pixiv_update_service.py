import json
import time
from dataclasses import dataclass
from typing import Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request

from app.services.pixiv import PixivClient, PixivRateLimitService


@dataclass
class PixivArtworkFetchResult:
    pixiv_id: str
    artwork_ids: list[str]
    artwork_ids_text: str


class PixivRequestReason:
    COOKIE_MISSING = "COOKIE_MISSING"
    COOKIE_EXPIRED = "COOKIE_EXPIRED"
    RATE_LIMIT = "RATE_LIMIT"
    NETWORK_ERROR = "NETWORK_ERROR"
    PARSE_ERROR = "PARSE_ERROR"
    PIXIV_RESPONSE_ERROR = "PIXIV_RESPONSE_ERROR"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"


REQUEST_REASON_LABELS = {
    PixivRequestReason.COOKIE_MISSING: "쿠키 누락",
    PixivRequestReason.COOKIE_EXPIRED: "쿠키 만료",
    PixivRequestReason.RATE_LIMIT: "요청 제한",
    PixivRequestReason.NETWORK_ERROR: "네트워크 오류",
    PixivRequestReason.PARSE_ERROR: "파싱 오류",
    PixivRequestReason.PIXIV_RESPONSE_ERROR: "Pixiv 응답 오류",
    PixivRequestReason.UNKNOWN_ERROR: "알 수 없는 오류",
}


class PixivRequestError(RuntimeError):
    def __init__(
        self,
        reason: str,
        message: str,
        should_stop: bool = False,
        retryable: bool = False,
    ):
        super().__init__(message)

        self.reason = reason
        self.message = message
        self.should_stop = should_stop
        self.retryable = retryable

    @property
    def reason_label(self) -> str:
        return REQUEST_REASON_LABELS.get(
            self.reason,
            REQUEST_REASON_LABELS[PixivRequestReason.UNKNOWN_ERROR],
        )

    def to_display_text(self) -> str:
        return f"[{self.reason_label}] {self.message}"


class PixivUpdateService:
    PIXIV_PROFILE_ALL_URL = (
        "https://www.pixiv.net/ajax/user/{pixiv_id}/profile/all"
    )
    PIXIV_ACCOUNT_URL = "https://www.pixiv.net/ajax/user/extra"

    DEFAULT_REQUEST_INTERVAL_MS = 2000
    DEFAULT_BATCH_SIZE = 1000
    DEFAULT_BATCH_REST_MS = 300000
    DEFAULT_RETRY_COUNT = 3
    REQUEST_TIMEOUT_SECONDS = 15

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

        self.rate_limit_service = PixivRateLimitService(
            request_interval_ms=self.request_interval_ms,
            batch_size=self.batch_size,
            batch_rest_ms=self.batch_rest_ms,
        )
        self.client = PixivClient(self.rate_limit_service)

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
        self.client.set_callbacks(
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
        last_error = None

        for attempt in range(self.retry_count + 1):
            try:
                return self._request_json(
                    url=url,
                    phpsessid=phpsessid,
                    referer=referer,
                    wait_before_request=wait_before_request,
                )
            except PixivRequestError as error:
                last_error = error

                if not error.retryable:
                    raise

                if attempt >= self.retry_count:
                    raise

                self._emit_retry_log(attempt + 1)
                self._wait_before_retry()

        if last_error is not None:
            raise last_error

        raise PixivRequestError(
            reason=PixivRequestReason.UNKNOWN_ERROR,
            message="Pixiv 요청 처리 중 알 수 없는 오류가 발생했습니다.",
            retryable=False,
        )

    def _emit_retry_log(
        self,
        attempt: int,
    ):
        self.rate_limit_service._emit_log(
            "재시도",
            f"Pixiv 요청 실패 후 재시도 중: {attempt}/{self.retry_count}",
        )

    def _wait_before_retry(self):
        time.sleep(self.request_interval_ms / 1000)

    def _request_json(
        self,
        url: str,
        phpsessid: str,
        referer: str,
        wait_before_request: bool = True,
    ) -> dict:
        if wait_before_request:
            request = self.client.build_request(
                url=url,
                phpsessid=phpsessid,
                referer=referer,
            )
        else:
            request = self._build_request_without_wait(
                url=url,
                phpsessid=phpsessid,
                referer=referer,
            )

        try:
            with self.client.open(
                request,
                timeout=self.REQUEST_TIMEOUT_SECONDS,
            ) as response:
                raw_body = response.read().decode("utf-8")
        except HTTPError as error:
            raise self._build_http_error(error) from error
        except TimeoutError as error:
            raise PixivRequestError(
                reason=PixivRequestReason.NETWORK_ERROR,
                message="Pixiv 요청 시간이 초과되었습니다.",
                retryable=True,
            ) from error
        except URLError as error:
            raise PixivRequestError(
                reason=PixivRequestReason.NETWORK_ERROR,
                message=f"Pixiv 연결 실패: {error.reason}",
                retryable=True,
            ) from error
        except Exception as error:
            raise PixivRequestError(
                reason=PixivRequestReason.UNKNOWN_ERROR,
                message=f"Pixiv 요청 실패: {error}",
                retryable=False,
            ) from error

        try:
            return json.loads(raw_body)
        except json.JSONDecodeError as error:
            raise PixivRequestError(
                reason=PixivRequestReason.PARSE_ERROR,
                message="Pixiv 응답을 JSON으로 해석하지 못했습니다.",
                retryable=False,
            ) from error

    def _build_request_without_wait(
        self,
        url: str,
        phpsessid: str,
        referer: str,
    ) -> Request:
        return self.client.build_request_without_wait(
            url=url,
            phpsessid=phpsessid,
            referer=referer,
        )

    def _build_http_error(
        self,
        error: HTTPError,
    ) -> PixivRequestError:
        if error.code == 429:
            return PixivRequestError(
                reason=PixivRequestReason.RATE_LIMIT,
                message="Pixiv 요청 제한이 발생했습니다. HTTP 429",
                should_stop=True,
                retryable=False,
            )

        if error.code == 403:
            return PixivRequestError(
                reason=PixivRequestReason.COOKIE_EXPIRED,
                message=(
                    "Pixiv 요청이 거부되었습니다. "
                    "PHPSESSID 만료 또는 요청 제한 가능성이 있습니다. "
                    "HTTP 403"
                ),
                should_stop=True,
                retryable=False,
            )

        if error.code in (500, 502, 503, 504):
            return PixivRequestError(
                reason=PixivRequestReason.NETWORK_ERROR,
                message=f"Pixiv 서버 오류: HTTP {error.code}",
                retryable=True,
            )

        return PixivRequestError(
            reason=PixivRequestReason.UNKNOWN_ERROR,
            message=f"Pixiv 요청 실패: HTTP {error.code}",
            retryable=False,
        )

    def _extract_artwork_ids(self, response_data: dict) -> list[str]:
        if response_data.get("error"):
            message = response_data.get("message") or "Pixiv 응답 오류"
            reason = self._classify_pixiv_error_message(message)

            raise PixivRequestError(
                reason=reason,
                message=message,
                should_stop=reason in (
                    PixivRequestReason.COOKIE_EXPIRED,
                    PixivRequestReason.RATE_LIMIT,
                ),
                retryable=False,
            )

        body = response_data.get("body")

        if not isinstance(body, dict):
            raise PixivRequestError(
                reason=PixivRequestReason.PARSE_ERROR,
                message="Pixiv 응답에 body 정보가 없습니다.",
                retryable=False,
            )

        artwork_ids = []

        artwork_ids.extend(
            self._extract_ids_from_dict(
                body.get("illusts")
            )
        )
        artwork_ids.extend(
            self._extract_ids_from_dict(
                body.get("manga")
            )
        )

        return list(dict.fromkeys(artwork_ids))

    def _classify_pixiv_error_message(
        self,
        message: str,
    ) -> str:
        lowered = str(message or "").lower()

        cookie_keywords = (
            "login",
            "logged in",
            "not logged",
            "unauthorized",
            "invalid",
            "expired",
            "cookie",
            "phpsessid",
        )

        rate_keywords = (
            "rate",
            "too many",
            "limit",
            "blocked",
            "forbidden",
        )

        if any(keyword in lowered for keyword in cookie_keywords):
            return PixivRequestReason.COOKIE_EXPIRED

        if any(keyword in lowered for keyword in rate_keywords):
            return PixivRequestReason.RATE_LIMIT

        return PixivRequestReason.PIXIV_RESPONSE_ERROR

    def _extract_ids_from_dict(
        self,
        value: Optional[dict],
    ) -> list[str]:
        if not isinstance(value, dict):
            return []

        return [
            str(artwork_id)
            for artwork_id in value.keys()
            if str(artwork_id).strip()
        ]

    def _sort_artwork_ids(
        self,
        artwork_ids: list[str],
    ) -> list[str]:
        return sorted(
            artwork_ids,
            key=self._sort_key,
            reverse=True,
        )

    def _sort_key(self, value: str):
        try:
            return int(value)
        except ValueError:
            return value
