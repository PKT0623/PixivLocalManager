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
