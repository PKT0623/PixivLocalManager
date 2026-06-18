from urllib.request import Request
from urllib.request import urlopen

from app.services.pixiv.rate_limit import (
    PixivRateLimitService,
)


class PixivClient:
    USER_AGENT = (
        "Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/120.0.0.0 "
        "Safari/537.36"
    )

    def __init__(
        self,
        rate_limit_service: PixivRateLimitService | None = None,
    ):
        self.rate_limit_service = (
            rate_limit_service
            or PixivRateLimitService()
        )

    def set_callbacks(
        self,
        log_callback=None,
        status_callback=None,
    ):
        self.rate_limit_service.set_callbacks(
            log_callback=log_callback,
            status_callback=status_callback,
        )

    def build_request(
        self,
        url: str,
        phpsessid: str,
        referer: str,
    ) -> Request:
        self.rate_limit_service.wait_before_request()

        return self.build_request_without_wait(
            url=url,
            phpsessid=phpsessid,
            referer=referer,
        )

    def build_request_without_wait(
        self,
        url: str,
        phpsessid: str,
        referer: str,
    ) -> Request:
        return Request(
            url,
            headers={
                "User-Agent": self.USER_AGENT,
                "Accept": "application/json",
                "Referer": referer,
                "Cookie": f"PHPSESSID={phpsessid}",
            },
        )

    def open(
        self,
        request: Request,
        timeout: int = 15,
    ):
        return urlopen(
            request,
            timeout=timeout,
        )
