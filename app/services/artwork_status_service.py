from dataclasses import dataclass
from typing import Optional


@dataclass
class ArtworkStatusResult:
    status: str
    local_count: int
    pixiv_count: int
    missing_count: int
    missing_ids: list[str]


class ArtworkStatusService:
    STATUS_UP_TO_DATE = "up_to_date"
    STATUS_NEED_UPDATE = "need_update"
    STATUS_UNKNOWN = "unknown"
    STATUS_ERROR = "error"

    def calculate_status(
        self,
        local_artwork_ids: Optional[str],
        pixiv_artwork_ids: Optional[str],
    ) -> ArtworkStatusResult:

        local_ids = self._parse_ids(local_artwork_ids)
        pixiv_ids = self._parse_ids(pixiv_artwork_ids)

        local_id_set = set(local_ids)
        pixiv_id_set = set(pixiv_ids)

        local_count = len(local_id_set)
        pixiv_count = len(pixiv_id_set)

        if pixiv_count == 0:
            return ArtworkStatusResult(
                status=self.STATUS_UNKNOWN,
                local_count=local_count,
                pixiv_count=0,
                missing_count=0,
                missing_ids=[],
            )

        missing_ids = sorted(
            pixiv_id_set - local_id_set,
            key=self._sort_key,
            reverse=True,
        )

        if missing_ids:
            status = self.STATUS_NEED_UPDATE
        else:
            status = self.STATUS_UP_TO_DATE

        return ArtworkStatusResult(
            status=status,
            local_count=local_count,
            pixiv_count=pixiv_count,
            missing_count=len(missing_ids),
            missing_ids=missing_ids,
        )

    def _parse_ids(self, raw: Optional[str]) -> list[str]:
        if not raw:
            return []

        return [
            value
            for value in (
                item.strip()
                for item in raw.split(",")
            )
            if value
        ]

    def _sort_key(self, value: str):
        try:
            return int(value)
        except ValueError:
            return value
