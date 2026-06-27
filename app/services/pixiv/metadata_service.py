import json
from datetime import datetime

from app.services.pixiv.metadata_parts import (
    PixivArtworkMetadata,
    PixivMetadataResponseParser,
    PixivMetadataTagParser,
    PixivUserMetadata,
)
from app.services.pixiv_update_service import (
    PixivRequestError,
    PixivRequestReason,
    PixivUpdateService,
)
from app.services.tag import TagService


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
        self.tag_parser = PixivMetadataTagParser()
        self.response_parser = PixivMetadataResponseParser(
            self.pixiv_update_service
        )

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
                referer=(
                    "https://www.pixiv.net/users/"
                    f"{pixiv_user_id}/illustrations"
                ),
            )
        except PixivRequestError as error:
            if error.reason in (
                PixivRequestReason.COOKIE_EXPIRED,
                PixivRequestReason.COOKIE_MISSING,
                PixivRequestReason.RATE_LIMIT,
            ):
                raise

            return "[]"
        except Exception:
            return "[]"

        tags = self.tag_parser.extract_user_illust_tag_statistics(
            response_data.get("body")
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
        ai_type = self._to_non_negative_int(body.get("aiType", 0))

        return PixivArtworkMetadata(
            artwork_id=artwork_id,
            title=str(body.get("title", "") or "").strip(),
            artist_id=str(body.get("userId", "") or "").strip(),
            artist_name=str(body.get("userName", "") or "").strip(),
            page_count=self._to_non_negative_int(
                body.get("pageCount", 0)
            ),
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
                PixivRequestReason.COOKIE_MISSING,
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
        return self.response_parser.get_body(response_data)

    def _extract_user_name(
        self,
        body: dict,
    ) -> str:
        return self.response_parser.extract_user_name(body)

    def _extract_user_tags_json(
        self,
        body: dict,
    ) -> str:
        tags = self.tag_parser.extract_user_tags(body)
        return self.tag_service.serialize_tags(tags)

    def _extract_artwork_tags_json(
        self,
        body: dict,
    ) -> str:
        tags = self.tag_parser.extract_artwork_tags(body)
        return self.tag_service.serialize_tags(
            tags,
            sort_tags=False,
        )

    def _normalize_tag_list(
        self,
        values: list,
    ) -> list[dict]:
        return self.tag_parser.normalize_tag_list(values)

    def _normalize_tag_dict(
        self,
        values: dict,
    ) -> list[dict]:
        return self.tag_parser.normalize_tag_dict(values)

    def _extract_translated_tag(
        self,
        item: dict,
    ) -> str:
        return self.tag_parser.extract_translated_tag(item)

    def _deduplicate_tags(
        self,
        tags: list[dict],
    ) -> list[dict]:
        return self.tag_parser.deduplicate_tags(tags)

    def _to_non_negative_int(
        self,
        value,
    ) -> int:
        return self.tag_parser.to_non_negative_int(value)

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
