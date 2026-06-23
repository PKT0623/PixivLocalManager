from collections import Counter


class StatisticsStatusService:
    STATUS_LABELS = {
        "up_to_date": "최신 상태",
        "latest": "최신 상태",
        "need_update": "업데이트 필요",
        "unknown": "미확인",
        "error": "오류",
    }

    STATUS_GROUPS = {
        "up_to_date": {"up_to_date", "latest"},
        "need_update": {"need_update"},
        "unknown": {"unknown"},
        "error": {"error"},
    }

    def get_status_statistics(self, artists: list[dict]) -> dict:
        total_count = len(artists)
        status_counter = Counter(
            str(artist.get("update_status", "") or "")
            for artist in artists
        )

        counts = {
            status_name: self.count_status(
                status_counter=status_counter,
                statuses=statuses,
            )
            for status_name, statuses in self.STATUS_GROUPS.items()
        }

        ratios = {
            status_name: self.calculate_ratio(
                count=count,
                total_count=total_count,
            )
            for status_name, count in counts.items()
        }

        return {
            "total_count": total_count,
            "counts": counts,
            "ratios": ratios,
            "labels": {
                status_name: self.STATUS_LABELS[status_name]
                for status_name in self.STATUS_GROUPS
            },
        }

    def count_status(
        self,
        status_counter: Counter,
        statuses: set[str],
    ) -> int:
        return sum(
            status_counter.get(status, 0)
            for status in statuses
        )

    def calculate_ratio(
        self,
        count: int,
        total_count: int,
    ) -> float:
        if total_count <= 0:
            return 0.0

        return round(
            count / total_count * 100,
            1,
        )
