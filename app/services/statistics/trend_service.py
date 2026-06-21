from collections import defaultdict
from datetime import datetime

from app.database.connection import get_connection
from app.database.update_history_utils import parse_ids


class StatisticsTrendService:
    DEFAULT_WEEK_LIMIT = 12

    def get_trend_statistics(self) -> dict:
        return {
            "weekly_change": self._get_weekly_change_statistics(),
        }

    def _get_weekly_change_statistics(self) -> list[dict]:
        missing_summary = self._get_weekly_missing_summary()
        size_summary = self._get_weekly_size_summary()

        week_keys = sorted(
            set(missing_summary.keys()) | set(size_summary.keys()),
            reverse=True,
        )

        rows = []

        for week_key in week_keys[:self.DEFAULT_WEEK_LIMIT]:
            missing_data = missing_summary.get(week_key, {})
            size_data = size_summary.get(week_key, {})

            rows.append(
                {
                    "week": self._format_week_label(week_key),
                    "missing_increase_count": missing_data.get(
                        "missing_increase_count",
                        0,
                    ),
                    "resolved_increase_count": missing_data.get(
                        "resolved_increase_count",
                        0,
                    ),
                    "folder_size_increase_bytes": size_data.get(
                        "folder_size_increase_bytes",
                        0,
                    ),
                }
            )

        return rows

    def _get_weekly_missing_summary(self) -> dict:
        histories_by_artist = defaultdict(list)

        for history in self._fetch_update_histories():
            artist_id = history.get("artist_id")

            if artist_id is None:
                continue

            histories_by_artist[artist_id].append(history)

        summary = defaultdict(
            lambda: {
                "missing_increase_count": 0,
                "resolved_increase_count": 0,
            }
        )

        for histories in histories_by_artist.values():
            histories.sort(
                key=lambda item: str(item.get("checked_at", ""))
            )

            previous_missing_ids = None

            for history in histories:
                checked_at = str(history.get("checked_at", "") or "")
                week_key = self._get_week_key(checked_at)

                if not week_key:
                    continue

                current_missing_ids = set(
                    parse_ids(history.get("missing_ids", ""))
                )

                if previous_missing_ids is None:
                    previous_missing_ids = current_missing_ids
                    continue

                new_missing_ids = current_missing_ids - previous_missing_ids
                resolved_missing_ids = (
                    previous_missing_ids - current_missing_ids
                )

                summary[week_key]["missing_increase_count"] += len(
                    new_missing_ids
                )
                summary[week_key]["resolved_increase_count"] += len(
                    resolved_missing_ids
                )

                previous_missing_ids = current_missing_ids

        return dict(summary)

    def _get_weekly_size_summary(self) -> dict:
        summary = defaultdict(
            lambda: {
                "folder_size_increase_bytes": 0,
            }
        )

        for artist in self._fetch_artist_size_rows():
            updated_at = str(artist.get("updated_at", "") or "")
            week_key = self._get_week_key(updated_at)

            if not week_key:
                continue

            summary[week_key]["folder_size_increase_bytes"] += int(
                artist.get("folder_size_bytes", 0) or 0
            )

        return dict(summary)

    def _fetch_update_histories(self) -> list[dict]:
        return self._fetch_all(
            """
            SELECT
                artist_id,
                checked_at,
                missing_ids
            FROM artist_update_history
            WHERE checked_at IS NOT NULL
              AND checked_at != ''
            ORDER BY artist_id ASC, checked_at ASC, id ASC
            """
        )

    def _fetch_artist_size_rows(self) -> list[dict]:
        return self._fetch_all(
            """
            SELECT
                updated_at,
                folder_size_bytes
            FROM artists
            WHERE updated_at IS NOT NULL
              AND updated_at != ''
              AND folder_size_bytes > 0
            """
        )

    def _fetch_all(
        self,
        query: str,
    ) -> list[dict]:
        with get_connection() as conn:
            cursor = conn.cursor()

            try:
                cursor.execute(query)
            except Exception:
                return []

            rows = cursor.fetchall()

        return [
            dict(row)
            for row in rows
        ]

    def _get_week_key(
        self,
        value: str,
    ) -> str:
        value = str(value or "").strip()

        if not value:
            return ""

        date_text = value[:10]

        try:
            date_value = datetime.fromisoformat(date_text).date()
        except ValueError:
            return ""

        week_of_month = ((date_value.day - 1) // 7) + 1

        return (
            f"{date_value.year}-"
            f"{date_value.month:02d}-"
            f"{week_of_month}"
        )

    def _format_week_label(
        self,
        week_key: str,
    ) -> str:
        parts = str(week_key or "").split("-")

        if len(parts) != 3:
            return str(week_key or "-")

        year, month, week = parts

        return f"{year}-{month}-{week}주차"
