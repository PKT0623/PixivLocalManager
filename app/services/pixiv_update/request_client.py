import json
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request

from app.services.pixiv import PixivClient, PixivRateLimitService

from .errors import PixivRequestError, PixivRequestReason


class PixivUpdateRequestClient:
    REQUEST_TIMEOUT_SECONDS = 15

    def __init__(
        self,
        request_interval_ms: int,
        batch_size: int,
        batch_rest_ms: int,
        retry_count: int,
    ):
        self.request_interval_ms = request_interval_ms
        self.batch_size = batch_size
        self.batch_rest_ms = batch_rest_ms
        self.retry_count = retry_count

        self.log_callback = None
        self.status_callback = None

        self.rate_limit_service = PixivRateLimitService(
            request_interval_ms=self.request_interval_ms,
            batch_size=self.batch_size,
            batch_rest_ms=self.batch_rest_ms,
        )
        self.client = PixivClient(self.rate_limit_service)

    def set_request_callbacks(
        self,
        log_callback=None,
        status_callback=None,
    ):
        self.log_callback = log_callback
        self.status_callback = status_callback

    def request_with_retry(
        self,
        url: str,
        phpsessid: str,
        referer: str,
        wait_before_request: bool = True,
    ) -> dict:
        last_error = None

        for attempt in range(self.retry_count + 1):
            try:
                return self.request_json(
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

                self.emit_retry_log(attempt + 1)
                self.wait_before_retry()

        if last_error is not None:
            raise last_error

        raise PixivRequestError(
            reason=PixivRequestReason.UNKNOWN_ERROR,
            message="Pixiv 요청 처리 중 알 수 없는 오류가 발생했습니다.",
            retryable=False,
        )

    def request_json(
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
            request = self.build_request_without_wait(
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
            raise self.build_http_error(error) from error
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

    def build_request_without_wait(
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

    def build_http_error(
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

    def emit_retry_log(
        self,
        attempt: int,
    ):
        if self.log_callback is None:
            return

        self.log_callback(
            "재시도",
            f"Pixiv 요청 실패 후 재시도 중: {attempt}/{self.retry_count}",
        )

    def wait_before_retry(self):
        time.sleep(self.request_interval_ms / 1000)
