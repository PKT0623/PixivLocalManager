from dataclasses import dataclass
from typing import Optional


@dataclass
class ArtworkStatusResult:
    status: str
    local_count: int
    pixiv_count: int
    missing_count: int


class ArtworkStatusService:
    STATUS_UP_TO_DATE = "up_to_date"
    STATUS_OUTDATED = "outdated"
    STATUS_UNKNOWN = "unknown"

    def calculate_status(
        self,
        local_artwork_ids: Optional[str],
        pixiv_artwork_ids: Optional[str],
    ) -> ArtworkStatusResult:

        local_ids = self._parse_ids(local_artwork_ids)
        pixiv_ids = self._parse_ids(pixiv_artwork_ids)

        local_count = len(local_ids)
        pixiv_count = len(pixiv_ids)

        if pixiv_count == 0:
            return ArtworkStatusResult(
                status=self.STATUS_UNKNOWN,
                local_count=local_count,
                pixiv_count=0,
                missing_count=0,
            )

        missing_count = max(pixiv_count - local_count, 0)

        if local_count >= pixiv_count:
            status = self.STATUS_UP_TO_DATE
        else:
            status = self.STATUS_OUTDATED

        return ArtworkStatusResult(
            status=status,
            local_count=local_count,
            pixiv_count=pixiv_count,
            missing_count=missing_count,
        )

    def _parse_ids(self, raw: Optional[str]) -> list[str]:
        if not raw:
            return []

        return [x.strip() for x in raw.split(",") if x.strip()]
