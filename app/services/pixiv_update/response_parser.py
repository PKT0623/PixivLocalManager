from typing import Optional

from .errors import PixivRequestError, PixivRequestReason


class PixivUpdateResponseParser:
    def extract_artwork_ids(
        self,
        response_data: dict,
    ) -> list[str]:
        if response_data.get("error"):
            message = response_data.get("message") or "Pixiv 응답 오류"
            reason = self.classify_pixiv_error_message(message)

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
            self.extract_ids_from_dict(
                body.get("illusts")
            )
        )
        artwork_ids.extend(
            self.extract_ids_from_dict(
                body.get("manga")
            )
        )

        return list(dict.fromkeys(artwork_ids))

    def classify_pixiv_error_message(
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

    def extract_ids_from_dict(
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

    def sort_artwork_ids(
        self,
        artwork_ids: list[str],
    ) -> list[str]:
        return sorted(
            artwork_ids,
            key=self.sort_key,
            reverse=True,
        )

    def sort_key(self, value: str):
        try:
            return int(value)
        except ValueError:
            return value
