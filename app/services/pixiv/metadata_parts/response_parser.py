from app.services.pixiv_update_service import (
    PixivRequestError,
    PixivRequestReason,
)


class PixivMetadataResponseParser:
    def __init__(self, pixiv_update_service):
        self.pixiv_update_service = pixiv_update_service

    def get_body(
        self,
        response_data: dict,
    ) -> dict:
        if response_data.get("error"):
            message = response_data.get("message") or "Pixiv 응답 오류"
            reason = self.pixiv_update_service._classify_pixiv_error_message(
                message
            )

            raise PixivRequestError(
                reason=reason,
                message=message,
                should_stop=False,
                retryable=False,
            )

        body = response_data.get("body")

        if not isinstance(body, dict):
            raise PixivRequestError(
                reason=PixivRequestReason.PARSE_ERROR,
                message="Pixiv 응답에 body 정보가 없습니다.",
                retryable=False,
            )

        return body

    def extract_user_name(
        self,
        body: dict,
    ) -> str:
        for key in (
            "name",
            "userName",
            "user_name",
        ):
            value = str(body.get(key, "") or "").strip()

            if value:
                return value

        return ""
