class UpdateCheckDataMixin:
    def load_artists(self):
        self.artists = self.artist_service.get_all_artists()
        self.artist_table.load_artists(self.artists)
        self.update_target_count()

    def update_target_count(self):
        artist_ids = self.selection_actions.get_selected_artist_ids()
        count = len(artist_ids)

        self.target_count_label.setText(f"확인 대상: {count}명")

        if count == 0:
            self.status_label.setText("")
        else:
            self.status_label.setText(f"업데이트 확인 대상: {count}명")

    def reset_summary(self):
        self.update_summary(
            {
                "total": 0,
                "latest": 0,
                "need_update": 0,
                "error": 0,
                "skipped": 0,
                "missing": 0,
            }
        )

    def update_summary(self, summary: dict):
        self.summary_total_label.setText(str(summary.get("total", 0)))
        self.summary_latest_label.setText(str(summary.get("latest", 0)))
        self.summary_need_update_label.setText(
            str(summary.get("need_update", 0))
        )
        self.summary_error_label.setText(str(summary.get("error", 0)))
        self.summary_skipped_label.setText(str(summary.get("skipped", 0)))
        self.summary_missing_label.setText(str(summary.get("missing", 0)))

    def shutdown_worker(self):
        self.actions.shutdown_worker()
