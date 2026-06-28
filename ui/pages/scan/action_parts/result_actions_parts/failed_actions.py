from pathlib import Path


class ScanResultFailedActionsMixin:
    def retry_failed_items(self):
        failed_rows = self.page.log_table.get_failed_rows()

        if not failed_rows:
            self.page.log_table.add_info_log("재시도할 실패 항목이 없습니다.")
            return

        self.clear_resume_state()

        folder_paths = []

        for row in failed_rows:
            folder_path = str(row.get("folder_path", "") or "").strip()

            if not folder_path:
                continue

            if folder_path in folder_paths:
                continue

            folder_paths.append(folder_path)

        if not folder_paths:
            self.page.log_table.add_info_log("재시도할 폴더 경로가 없습니다.")
            return

        root_folder = self.page.folder_section.folder_path_input.text().strip()

        if not root_folder:
            root_folder = str(Path(folder_paths[0]).parent)

        self.page.settings_service.set_setting(
            "last_scan_folder",
            root_folder,
        )

        self.page.log_table.clear_failed_rows()
        self.page.log_table.add_info_log(
            f"실패 항목 재시도 시작: {len(folder_paths)}개"
        )

        self._start_worker(
            folder_path=root_folder,
            target_folder_paths=folder_paths,
            clear_log=False,
            preview_mode=False,
            resume_payload=None,
        )

    def clear_failed_items(self):
        self.page.log_table.clear_failed_rows()
        self.page.log_table.add_info_log("실패 목록을 초기화했습니다.")

    def _collect_non_artwork_files_from_preview(self) -> list[dict]:
        rows = self.page.preview_table.get_all_preview_rows()
        records = []
        seen_keys = set()

        for row in rows:
            row_records = row.get("non_artwork_files", [])

            if not isinstance(row_records, list):
                continue

            for record in row_records:
                if not isinstance(record, dict):
                    continue

                file_path = str(record.get("file_path", "") or "")
                reason = str(record.get("reason", "") or "")
                key = (file_path, reason)

                if key in seen_keys:
                    continue

                seen_keys.add(key)
                records.append(record)

        return records
