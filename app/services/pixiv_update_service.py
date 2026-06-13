import json
import random
import time
from dataclasses import dataclass
from typing import Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


@dataclass
class PixivArtworkFetchResult:
    pixiv_id: str
    artwork_ids: list[str]
    artwork_ids_text: str


class PixivUpdateService:
    PIXIV_PROFILE_ALL_URL = (
        "https://www.pixiv.net/ajax/user/{pixiv_id}/profile/all"
    )

    MIN_REQUEST_INTERVAL_SECONDS = 3
    MAX_REQUEST_INTERVAL_SECONDS = 6

    def __init__(self):
        self.last_request_time = 0.0

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
            raise ValueError("Pixiv PHPSESSID가 없습니다.")

        self._wait_before_request()

        response_data = self._request_profile_all(
            pixiv_id,
            phpsessid,
        )

        artwork_ids = self._extract_artwork_ids(response_data)
        artwork_ids = self._sort_artwork_ids(artwork_ids)

        return PixivArtworkFetchResult(
            pixiv_id=pixiv_id,
            artwork_ids=artwork_ids,
            artwork_ids_text=",".join(artwork_ids),
        )

    def _wait_before_request(self):
        now = time.time()
        elapsed = now - self.last_request_time

        wait_seconds = random.uniform(
            self.MIN_REQUEST_INTERVAL_SECONDS,
            self.MAX_REQUEST_INTERVAL_SECONDS,
        )

        remaining = wait_seconds - elapsed

        if remaining > 0:
            time.sleep(remaining)

        self.last_request_time = time.time()

    def _request_profile_all(
        self,
        pixiv_id: str,
        phpsessid: str,
    ) -> dict:
        url = self.PIXIV_PROFILE_ALL_URL.format(
            pixiv_id=pixiv_id,
        )

        request = Request(
            url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
                "Accept": "application/json",
                "Referer": f"https://www.pixiv.net/users/{pixiv_id}",
                "Cookie": f"PHPSESSID={phpsessid}",
            },
        )

        try:
            with urlopen(request, timeout=15) as response:
                raw_body = response.read().decode("utf-8")
        except HTTPError as error:
            if error.code in (403, 429):
                raise RuntimeError(
                    f"Pixiv 요청 중단 필요: HTTP {error.code}"
                ) from error

            raise RuntimeError(
                f"Pixiv 요청 실패: HTTP {error.code}"
            ) from error
        except URLError as error:
            raise RuntimeError(
                f"Pixiv 연결 실패: {error.reason}"
            ) from error
        except TimeoutError as error:
            raise RuntimeError("Pixiv 요청 시간이 초과되었습니다.") from error

        try:
            return json.loads(raw_body)
        except json.JSONDecodeError as error:
            raise RuntimeError("Pixiv 응답을 JSON으로 해석하지 못했습니다.") from error

    def _extract_artwork_ids(self, response_data: dict) -> list[str]:
        if response_data.get("error"):
            message = response_data.get("message") or "Pixiv 응답 오류"
            raise RuntimeError(message)

        body = response_data.get("body")

        if not isinstance(body, dict):
            raise RuntimeError("Pixiv 응답에 body 정보가 없습니다.")

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
