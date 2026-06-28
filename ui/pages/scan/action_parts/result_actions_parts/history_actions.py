import json


class ScanResultHistoryActionsMixin:
    def load_scan_history(self):
        last_scan_result = self._load_json_setting("last_scan_result")
        recent_scan_history = self._load_json_setting("recent_scan_history")

        if not isinstance(recent_scan_history, list):
            recent_scan_history = []

        compare_result = self._build_latest_compare_result(
            recent_scan_history
        )

        self.page.progress_section.update_last_scan_info(last_scan_result)
        self.page.progress_section.update_recent_scan_history(
            recent_scan_history
        )
        self.page.progress_section.update_scan_compare_info(compare_result)

    def _save_scan_result(
        self,
        result: dict,
    ):
        rows = list(self.page.log_table.all_rows)
        payload = {
            "summary": result,
            "rows": rows,
        }

        self._save_json_setting("last_scan_result", result)
        self._save_recent_scan_history(result)
        self._save_latest_scan_files(payload)

    def _save_recent_scan_history(
        self,
        result: dict,
    ):
        history = self._load_json_setting("recent_scan_history")

        if not isinstance(history, list):
            history = []

        history.insert(0, result)
        history = history[:self.RECENT_HISTORY_LIMIT]

        self._save_json_setting("recent_scan_history", history)

    def _save_latest_scan_files(
        self,
        payload: dict,
    ):
        self.SCAN_RESULT_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        with open(
            self.LATEST_SCAN_JSON_PATH,
            "w",
            encoding="utf-8",
        ) as json_file:
            json.dump(
                payload,
                json_file,
                ensure_ascii=False,
                indent=2,
            )

        self._write_rows_csv(
            self.LATEST_SCAN_CSV_PATH,
            payload.get("rows", []),
        )
