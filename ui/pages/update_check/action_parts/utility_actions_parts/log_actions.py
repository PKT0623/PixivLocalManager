import csv
from datetime import datetime
from pathlib import Path


class UpdateCheckLogActionsMixin:
    def export_log_csv(self):
        if self.page.log_table.rowCount() == 0:
            self.page.status_label.setText("저장할 결과 로그가 없습니다.")
            return

        export_dir = Path("exports") / "update_logs"
        export_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = export_dir / f"update_check_log_{timestamp}.csv"

        headers, rows = self.page.log_table.get_csv_data()

        with file_path.open(
            "w",
            encoding="utf-8-sig",
            newline="",
        ) as file:
            writer = csv.writer(file)
            writer.writerow(headers)
            writer.writerows(rows)

        self.page.status_label.setText(
            f"CSV 저장 완료: {file_path}"
        )

    def update_log_action_buttons(self):
        if self._is_log_action_locked():
            self._set_log_action_buttons_enabled(False)
            return

        selected_artist_ids = self.page.log_table.get_selected_artist_ids()
        missing_artist_ids = self.page.log_table.get_missing_artist_ids()
        error_artist_ids = self.page.log_table.get_error_artist_ids()
        download_rows = self.page.log_table.get_download_candidate_rows()
        has_logs = self.page.log_table.rowCount() > 0

        has_selected_artist = bool(selected_artist_ids)
        has_single_selected_artist = len(selected_artist_ids) == 1

        self.page.open_log_artist_detail_button.setEnabled(
            has_single_selected_artist
        )
        self.page.open_log_artist_list_button.setEnabled(
            has_selected_artist
        )
        self.page.rescan_selected_log_button.setEnabled(
            has_selected_artist
        )
        self.page.rescan_missing_log_button.setEnabled(
            bool(missing_artist_ids)
        )
        self.page.rescan_error_log_button.setEnabled(
            bool(error_artist_ids)
        )
        self.page.export_download_txt_button.setEnabled(
            bool(download_rows)
        )
        self.page.export_download_csv_button.setEnabled(
            bool(download_rows)
        )
        self.page.export_csv_button.setEnabled(has_logs)

    def open_log_artist_detail_by_id(
        self,
        artist_id: int,
    ):
        if self._is_log_action_locked():
            return

        self.page.artist_detail_requested.emit(artist_id)

    def open_selected_log_artist_detail(self):
        if self._is_log_action_locked():
            return

        artist_ids = self.page.log_table.get_selected_artist_ids()

        if not artist_ids:
            self.page.status_label.setText("상세로 열 작가를 선택하세요.")
            return

        self.page.artist_detail_requested.emit(artist_ids[0])

    def open_selected_log_artist_list(self):
        if self._is_log_action_locked():
            return

        artist_ids = self.page.log_table.get_selected_artist_ids()

        if not artist_ids:
            self.page.status_label.setText("목록에서 볼 작가를 선택하세요.")
            return

        self.page.artist_list_requested.emit(artist_ids)

    def _is_log_action_locked(self) -> bool:
        if self._is_worker_running():
            return True

        if getattr(self, "is_paused", False):
            return True

        return False

    def _set_log_action_buttons_enabled(
        self,
        enabled: bool,
    ):
        buttons = [
            self.page.open_log_artist_detail_button,
            self.page.open_log_artist_list_button,
            self.page.rescan_selected_log_button,
            self.page.rescan_missing_log_button,
            self.page.rescan_error_log_button,
            self.page.export_download_txt_button,
            self.page.export_download_csv_button,
        ]

        for button in buttons:
            button.setEnabled(enabled)
