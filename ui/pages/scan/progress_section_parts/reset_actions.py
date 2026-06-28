class ScanProgressResetActionsMixin:
    def reset(self):
        self.update_scan_state("대기")

        self.target_count_label.setText(
            "발견된 작가 폴더: -"
        )
        self.current_folder_label.setText(
            "현재 작업: -"
        )

        self.progress_bar.setRange(
            0,
            100,
        )
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("0 / 0")

        self.scan_start_time_label.setText("시작 시각: -")
        self.elapsed_time_label.setText("경과 시간: -")
        self.scan_speed_label.setText("진행 속도: -")
        self.estimated_time_label.setText("예상 남은 시간: -")

        self.update_summary(
            {
                "created": 0,
                "updated": 0,
                "unchanged": 0,
                "failed": 0,
            }
        )
        self.update_statistics(
            {
                "total_file_count": 0,
                "total_artwork_count": 0,
                "extension_counts": {},
                "non_artwork_file_count": 0,
                "unsupported_extension_count": 0,
                "artwork_id_not_found_count": 0,
                "empty_file_count": 0,
                "scan_error_count": 0,
            }
        )

    def reset_progress_only(self):
        self.update_scan_state("대기")
        self.target_count_label.setText(
            "발견된 작가 폴더: -"
        )
        self.current_folder_label.setText(
            "현재 작업: -"
        )
        self.progress_bar.setRange(
            0,
            100,
        )
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("0 / 0")
