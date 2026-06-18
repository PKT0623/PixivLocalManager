import json
from dataclasses import dataclass
from datetime import datetime

from app.services.pixiv_update_service import (
    PixivRequestError,
    PixivRequestReason,
    PixivUpdateService,
)
from app.services.tag import TagService


@dataclass
class PixivUserMetadata:
    pixiv_user_id: str
    user_name: str
    artwork_count: int
    pixiv_tags: str


@dataclass
class PixivArtworkMetadata:
    artwork_id: str
    title: str
    artist_id: str
    artist_name: str
    page_count: int
    ai_type: int
    is_ai_generated: bool
    pixiv_tags: str


class PixivMetadataService:
    PIXIV_USER_URL = "https://www.pixiv.net/ajax/user/{pixiv_user_id}"
    PIXIV_USER_ILLUST_TAGS_URL = (
        "https://www.pixiv.net/ajax/user/{pixiv_user_id}/illusts/tags"
        "?all=1&lang=ko"
    )
    PIXIV_ARTWORK_URL = "https://www.pixiv.net/ajax/illust/{artwork_id}"

    def __init__(
        self,
        pixiv_update_service: PixivUpdateService | None = None,
    ):
        self.pixiv_update_service = (
            pixiv_update_service
            or PixivUpdateService()
        )
        self.tag_service = TagService()

    def fetch_user_metadata(
        self,
        pixiv_user_id: str,
        phpsessid: str,
    ) -> PixivUserMetadata:
        pixiv_user_id = str(pixiv_user_id or "").strip()

        if not pixiv_user_id:
            raise ValueError("Pixiv 유저 ID가 비어 있습니다.")

        user_data = self._request_json(
            url=self.PIXIV_USER_URL.format(
                pixiv_user_id=pixiv_user_id,
            ),
            phpsessid=phpsessid,
            referer=f"https://www.pixiv.net/users/{pixiv_user_id}",
        )

        user_body = self._get_body(user_data)
        user_name = self._extract_user_name(user_body)
        artwork_count = self._extract_artwork_count_safely(
            pixiv_user_id=pixiv_user_id,
            phpsessid=phpsessid,
        )
        pixiv_tags = self.fetch_user_illust_tag_statistics(
            pixiv_user_id=pixiv_user_id,
            phpsessid=phpsessid,
        )

        return PixivUserMetadata(
            pixiv_user_id=pixiv_user_id,
            user_name=user_name,
            artwork_count=artwork_count,
            pixiv_tags=pixiv_tags,
        )

    def fetch_user_illust_tag_statistics(
        self,
        pixiv_user_id: str,
        phpsessid: str,
    ) -> str:
        pixiv_user_id = str(pixiv_user_id or "").strip()

        if not pixiv_user_id:
            return "[]"

        try:
            response_data = self._request_json(
                url=self.PIXIV_USER_ILLUST_TAGS_URL.format(
                    pixiv_user_id=pixiv_user_id,
                ),
                phpsessid=phpsessid,
                referer=f"https://www.pixiv.net/users/{pixiv_user_id}/illustrations",
            )
        except Exception:
            return "[]"

        body = response_data.get("body")

        if not isinstance(body, list):
            return "[]"

        tags = []

        for item in body:
            if not isinstance(item, dict):
                continue

            original = str(item.get("tag", "") or "").strip()

            if not original:
                continue

            translated = str(
                item.get("tag_translation", "")
                or item.get("translated", "")
                or item.get("translated_name", "")
                or ""
            ).strip()

            count = self._to_non_negative_int(
                item.get("cnt")
                or item.get("count")
                or item.get("artwork_count")
                or 0
            )

            tags.append(
                {
                    "original": original,
                    "translated": translated,
                    "artwork_count": count,
                    "custom_translation": False,
                }
            )

        return self.tag_service.serialize_tags(tags)

    def fetch_artwork_metadata(
        self,
        artwork_id: str,
        phpsessid: str,
    ) -> PixivArtworkMetadata:
        artwork_id = str(artwork_id or "").strip()

        if not artwork_id:
            raise ValueError("작품 ID가 비어 있습니다.")

        artwork_data = self._request_json(
            url=self.PIXIV_ARTWORK_URL.format(
                artwork_id=artwork_id,
            ),
            phpsessid=phpsessid,
            referer=f"https://www.pixiv.net/artworks/{artwork_id}",
        )

        body = self._get_body(artwork_data)
        ai_type = int(body.get("aiType", 0) or 0)

        return PixivArtworkMetadata(
            artwork_id=artwork_id,
            title=str(body.get("title", "") or "").strip(),
            artist_id=str(body.get("userId", "") or "").strip(),
            artist_name=str(body.get("userName", "") or "").strip(),
            page_count=int(body.get("pageCount", 0) or 0),
            ai_type=ai_type,
            is_ai_generated=ai_type == 2,
            pixiv_tags=self._extract_artwork_tags_json(body),
        )

    def _extract_artwork_count_safely(
        self,
        pixiv_user_id: str,
        phpsessid: str,
    ) -> int:
        try:
            profile_data = self.pixiv_update_service.fetch_artist_artwork_ids(
                pixiv_id=pixiv_user_id,
                phpsessid=phpsessid,
            )
            return len(profile_data.artwork_ids)
        except PixivRequestError as error:
            if error.reason in (
                PixivRequestReason.COOKIE_EXPIRED,
                PixivRequestReason.RATE_LIMIT,
            ):
                raise

            return 0
        except Exception:
            return 0

    def _request_json(
        self,
        url: str,
        phpsessid: str,
        referer: str,
    ) -> dict:
        return self.pixiv_update_service._request_with_retry(
            url=url,
            phpsessid=phpsessid,
            referer=referer,
        )

    def _get_body(
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

    def _extract_user_name(
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

    def _extract_user_tags_json(
        self,
        body: dict,
    ) -> str:
        tags = []

        for key in (
            "tags",
            "tag",
            "popularTags",
            "workspaceTags",
        ):
            value = body.get(key)

            if isinstance(value, list):
                tags.extend(self._normalize_tag_list(value))
            elif isinstance(value, dict):
                tags.extend(self._normalize_tag_dict(value))

        return self.tag_service.serialize_tags(tags)

    def _extract_artwork_tags_json(
        self,
        body: dict,
    ) -> str:
        tag_container = body.get("tags", {})
        raw_tags = []

        if isinstance(tag_container, dict):
            raw_tags = tag_container.get("tags", [])

        if not isinstance(raw_tags, list):
            raw_tags = []

        tags = []

        for item in raw_tags:
            if not isinstance(item, dict):
                continue

            original = str(item.get("tag", "") or "").strip()

            if not original:
                continue

            translated = self._extract_translated_tag(item)

            tags.append(
                {
                    "original": original,
                    "translated": translated,
                    "artwork_count": 0,
                    "custom_translation": False,
                }
            )

        return self.tag_service.serialize_tags(tags)

    def _normalize_tag_list(
        self,
        values: list,
    ) -> list[dict]:
        tags = []

        for item in values:
            if isinstance(item, str):
                original = item.strip()

                if original:
                    tags.append(
                        {
                            "original": original,
                            "translated": "",
                            "artwork_count": 0,
                            "custom_translation": False,
                        }
                    )

                continue

            if not isinstance(item, dict):
                continue

            original = str(
                item.get("tag")
                or item.get("name")
                or item.get("original")
                or ""
            ).strip()

            if not original:
                continue

            translated = self._extract_translated_tag(item)
            count = self._to_non_negative_int(
                item.get("cnt")
                or item.get("count")
                or item.get("total")
                or item.get("artwork_count")
                or 0
            )

            tags.append(
                {
                    "original": original,
                    "translated": translated,
                    "artwork_count": count,
                    "custom_translation": False,
                }
            )

        return tags

    def _normalize_tag_dict(
        self,
        values: dict,
    ) -> list[dict]:
        tags = []

        for original, raw_value in values.items():
            original = str(original or "").strip()

            if not original:
                continue

            count = 0
            translated = ""

            if isinstance(raw_value, dict):
                translated = self._extract_translated_tag(raw_value)
                count = self._to_non_negative_int(
                    raw_value.get("cnt")
                    or raw_value.get("count")
                    or raw_value.get("total")
                    or raw_value.get("artwork_count")
                    or 0
                )
            elif isinstance(raw_value, int):
                count = raw_value

            tags.append(
                {
                    "original": original,
                    "translated": translated,
                    "artwork_count": count,
                    "custom_translation": False,
                }
            )

        return tags

    def _extract_translated_tag(
        self,
        item: dict,
    ) -> str:
        translation = item.get("translation")

        if isinstance(translation, dict):
            for value in translation.values():
                text = str(value or "").strip()

                if text:
                    return text

        for key in (
            "tag_translation",
            "translated",
            "translated_name",
            "romaji",
        ):
            text = str(item.get(key, "") or "").strip()

            if text:
                return text

        return ""

    def _deduplicate_tags(
        self,
        tags: list[dict],
    ) -> list[dict]:
        result = []
        seen = set()

        for tag in tags:
            original = str(tag.get("original", "") or "").strip()

            if not original or original in seen:
                continue

            seen.add(original)
            result.append(tag)

        return result

    def _to_non_negative_int(
        self,
        value,
    ) -> int:
        try:
            return max(0, int(value))
        except (TypeError, ValueError):
            return 0

    def to_json(
        self,
        tags: list[dict],
    ) -> str:
        return json.dumps(
            tags,
            ensure_ascii=False,
        )

    def get_current_timestamp(self) -> str:
        return datetime.now().isoformat()
