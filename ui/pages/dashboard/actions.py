from app.database import (
    ArtistUpdateHistoryRepository,
    BookmarkArtworkRepository,
    FollowUserRepository,
)

from .dashboard_metrics import (
    build_recent_activity_data,
    build_scan_statistics_data,
    build_top_ranking_data,
    calculate_dashboard_summary,
    calculate_update_status_summary,
)


class DashboardActions:
    RECENT_ACTIVITY_LIMIT = 50

    def __init__(self, page):
        self.page = page
        self.history_repo = ArtistUpdateHistoryRepository()
        self.follow_user_repo = FollowUserRepository()
        self.bookmark_artwork_repo = BookmarkArtworkRepository()

    def load_dashboard(self):
        artists = self.page.artist_service.get_all_artists()
        valid_artist_ids = self._get_valid_artist_ids(artists)

        recent_histories = self._filter_latest_history_per_artist(
            self._filter_existing_artist_histories(
                self.history_repo.get_recent(
                    limit=self.RECENT_ACTIVITY_LIMIT * 5,
                ),
                valid_artist_ids,
            )
        )[: self.RECENT_ACTIVITY_LIMIT]
        today_histories = self._filter_existing_artist_histories(
            self.history_repo.get_today_histories(),
            valid_artist_ids,
        )
        latest_histories = self._filter_existing_artist_histories(
            self.history_repo.get_latest_history_per_artist(),
            valid_artist_ids,
        )
        recent_error_histories = self._filter_existing_artist_histories(
            self.history_repo.get_recent_error_histories(
                limit=self.RECENT_ACTIVITY_LIMIT * 3,
            ),
            valid_artist_ids,
        )[: self.RECENT_ACTIVITY_LIMIT]
        missing_increased_histories = self._filter_existing_artist_histories(
            self.history_repo.get_recent_missing_increased_artists(
                limit=self.RECENT_ACTIVITY_LIMIT * 3,
            ),
            valid_artist_ids,
        )[: self.RECENT_ACTIVITY_LIMIT]

        self.page.current_artists = artists

        update_status_summary = calculate_update_status_summary(
            artists=artists,
            today_histories=today_histories,
            latest_histories=latest_histories,
            history_repo=self.history_repo,
        )
        summary = self.calculate_summary(
            artists=artists,
            update_status_summary=update_status_summary,
        )
        recent_activity_data = build_recent_activity_data(
            artists=artists,
            recent_histories=recent_histories,
            recent_error_histories=recent_error_histories,
            missing_increased_histories=missing_increased_histories,
            limit=self.RECENT_ACTIVITY_LIMIT,
        )
        scan_statistics_data = build_scan_statistics_data(
            recent_histories=recent_histories,
        )
        top_ranking_data = build_top_ranking_data(
            artists=artists,
        )

        self.page.summary_section.update_summary(summary)
        self.page.update_status_section.update_status_summary(
            update_status_summary
        )
        self.page.recent_activity_section.update_recent_activity(
            recent_activity_data
        )
        self.page.scan_statistics_section.update_scan_statistics(
            scan_statistics_data
        )
        self.page.top_ranking_section.update_top_rankings(top_ranking_data)
        self.page.recommendation_section.update_recommendations(artists)
        self.page.random_artist_section.update_artists(artists)

    def calculate_summary(
        self,
        artists: list[dict],
        update_status_summary: dict,
    ) -> dict:
        return calculate_dashboard_summary(
            artists=artists,
            update_status_summary=update_status_summary,
            follow_user_count=self._count_follow_users(),
            bookmark_artwork_count=self._count_bookmark_artworks(),
        )

    def _get_valid_artist_ids(self, artists: list[dict]) -> set[int]:
        valid_artist_ids = set()

        for artist in artists:
            artist_id = artist.get("id")

            if artist_id is None:
                continue

            try:
                valid_artist_ids.add(int(artist_id))
            except (TypeError, ValueError):
                continue

        return valid_artist_ids

    def _filter_existing_artist_histories(
        self,
        histories: list[dict],
        valid_artist_ids: set[int],
    ) -> list[dict]:
        filtered_histories = []

        for history in histories:
            artist_id = history.get("artist_id")

            if artist_id is None:
                continue

            try:
                normalized_artist_id = int(artist_id)
            except (TypeError, ValueError):
                continue

            if normalized_artist_id not in valid_artist_ids:
                continue

            filtered_histories.append(history)

        return filtered_histories

    def _filter_latest_history_per_artist(
        self,
        histories: list[dict],
    ) -> list[dict]:
        latest_history_map = {}

        for history in histories:
            artist_id = history.get("artist_id")

            if artist_id is None:
                continue

            try:
                normalized_artist_id = int(artist_id)
            except (TypeError, ValueError):
                continue

            current_history = latest_history_map.get(normalized_artist_id)

            if current_history is None:
                latest_history_map[normalized_artist_id] = history
                continue

            if self._is_newer_history(history, current_history):
                latest_history_map[normalized_artist_id] = history

        return sorted(
            latest_history_map.values(),
            key=lambda history: (
                str(history.get("checked_at", "") or ""),
                self._to_int(history.get("id", 0)),
            ),
            reverse=True,
        )

    def _is_newer_history(
        self,
        history: dict,
        target_history: dict,
    ) -> bool:
        history_checked_at = str(history.get("checked_at", "") or "")
        target_checked_at = str(target_history.get("checked_at", "") or "")

        if history_checked_at != target_checked_at:
            return history_checked_at > target_checked_at

        history_id = self._to_int(history.get("id", 0))
        target_history_id = self._to_int(target_history.get("id", 0))

        return history_id > target_history_id

    def _count_follow_users(self) -> int:
        return len(self.follow_user_repo.get_all())

    def _count_bookmark_artworks(self) -> int:
        return len(self.bookmark_artwork_repo.get_all())

    def _to_int(self, value, default: int = 0) -> int:
        try:
            return int(value)
        except (TypeError, ValueError):
            return default
