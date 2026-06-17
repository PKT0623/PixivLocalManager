from collections import defaultdict
from pathlib import Path

from app.database.artist import ArtistRepository


class DatabaseIntegrityService:
    VALID_STATUSES = {
        "normal",
        "active",
        "inactive",
    }

    VALID_UPDATE_STATUSES = {
        "unknown",
        "latest",
        "up_to_date",
        "need_update",
        "updated",
        "error",
    }

    def __init__(self):
        self.artist_repo = ArtistRepository()

    def check_integrity(self) -> dict:
        artists = self.artist_repo.get_all()

        issues = []
        issues.extend(self._check_duplicate_pixiv_ids(artists))
        issues.extend(self._check_missing_folders(artists))
        issues.extend(self._check_empty_artist_names(artists))
        issues.extend(self._check_invalid_ratings(artists))
        issues.extend(self._check_invalid_statuses(artists))
        issues.extend(self._check_invalid_update_statuses(artists))

        return {
            "ok": len(issues) == 0,
            "issue_count": len(issues),
            "issues": issues,
        }

    def _check_duplicate_pixiv_ids(
        self,
        artists: list[dict],
    ) -> list[dict]:
        pixiv_id_map = defaultdict(list)

        for artist in artists:
            pixiv_id = str(artist.get("pixiv_id", "") or "").strip()

            if not pixiv_id:
                continue

            pixiv_id_map[pixiv_id].append(artist)

        issues = []

        for pixiv_id, duplicated_artists in pixiv_id_map.items():
            if len(duplicated_artists) <= 1:
                continue

            for artist in duplicated_artists:
                issues.append(
                    self._build_issue(
                        issue_type="중복 Pixiv ID",
                        artist=artist,
                        detail=f"Pixiv ID {pixiv_id}가 중복되었습니다.",
                    )
                )

        return issues

    def _check_missing_folders(
        self,
        artists: list[dict],
    ) -> list[dict]:
        issues = []

        for artist in artists:
            folder_path = str(artist.get("folder_path", "") or "").strip()

            if not folder_path:
                issues.append(
                    self._build_issue(
                        issue_type="폴더 경로 없음",
                        artist=artist,
                        detail="폴더 경로가 비어 있습니다.",
                    )
                )
                continue

            if not Path(folder_path).exists():
                issues.append(
                    self._build_issue(
                        issue_type="존재하지 않는 폴더",
                        artist=artist,
                        detail=folder_path,
                    )
                )

        return issues

    def _check_empty_artist_names(
        self,
        artists: list[dict],
    ) -> list[dict]:
        issues = []

        for artist in artists:
            artist_name = str(artist.get("artist_name", "") or "").strip()

            if artist_name:
                continue

            issues.append(
                self._build_issue(
                    issue_type="빈 작가명",
                    artist=artist,
                    detail="작가명이 비어 있습니다.",
                )
            )

        return issues

    def _check_invalid_ratings(
        self,
        artists: list[dict],
    ) -> list[dict]:
        issues = []

        for artist in artists:
            rating = artist.get("rating", 0)

            try:
                rating = int(rating)
            except (TypeError, ValueError):
                issues.append(
                    self._build_issue(
                        issue_type="잘못된 평점",
                        artist=artist,
                        detail=f"평점 값이 숫자가 아닙니다: {rating}",
                    )
                )
                continue

            if rating < 0 or rating > 10:
                issues.append(
                    self._build_issue(
                        issue_type="잘못된 평점",
                        artist=artist,
                        detail=f"평점 범위 초과: {rating}",
                    )
                )

        return issues

    def _check_invalid_statuses(
        self,
        artists: list[dict],
    ) -> list[dict]:
        issues = []

        for artist in artists:
            status = str(artist.get("status", "") or "").strip()

            if status in self.VALID_STATUSES:
                continue

            issues.append(
                self._build_issue(
                    issue_type="잘못된 status",
                    artist=artist,
                    detail=f"허용되지 않은 status: {status}",
                )
            )

        return issues

    def _check_invalid_update_statuses(
        self,
        artists: list[dict],
    ) -> list[dict]:
        issues = []

        for artist in artists:
            update_status = str(
                artist.get("update_status", "") or ""
            ).strip()

            if update_status in self.VALID_UPDATE_STATUSES:
                continue

            issues.append(
                self._build_issue(
                    issue_type="잘못된 update_status",
                    artist=artist,
                    detail=f"허용되지 않은 update_status: {update_status}",
                )
            )

        return issues

    def _build_issue(
        self,
        issue_type: str,
        artist: dict,
        detail: str,
    ) -> dict:
        return {
            "type": issue_type,
            "artist_id": artist.get("id", "-"),
            "artist_name": artist.get("artist_name", "-") or "-",
            "pixiv_id": artist.get("pixiv_id", "-") or "-",
            "detail": detail,
        }
