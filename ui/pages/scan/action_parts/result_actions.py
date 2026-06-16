import csv
import json
from pathlib import Path

from PySide6.QtWidgets import QFileDialog


class ScanResultActions:
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

    def export_failed_items_csv(self):
        failed_rows = self.page.log_table.get_failed_rows()

        if not failed_rows:
            self.page.log_table.add_info_log(
                "CSV로 저장할 실패 항목이 없습니다."
            )
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self.page,
            "실패 항목 CSV 저장",
            "scan_failed_items.csv",
            "CSV Files (*.csv)",
        )

        if not file_path:
            return

        try:
            self._write_rows_csv(file_path, failed_rows)
        except Exception as error:
            self.page.log_table.add_info_log(
                f"실패 항목 CSV 저장 실패: {error}"
            )
            return

        self.page.log_table.add_info_log(
            f"실패 항목 CSV 저장 완료: {file_path}"
        )

    def export_all_scan_results_csv(self):
        rows = list(self.page.log_table.all_rows)

        if not rows:
            self.page.log_table.add_info_log("CSV로 저장할 결과가 없습니다.")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self.page,
            "스캔 결과 CSV 저장",
            "scan_results.csv",
            "CSV Files (*.csv)",
        )

        if not file_path:
            return

        try:
            self._write_rows_csv(file_path, rows)
        except Exception as error:
            self.page.log_table.add_info_log(
                f"스캔 결과 CSV 저장 실패: {error}"
            )
            return

        self.page.log_table.add_info_log(
            f"스캔 결과 CSV 저장 완료: {file_path}"
        )

    def export_preview_results_csv(self):
        rows = self.page.preview_table.get_all_preview_rows()

        if not rows:
            self.page.log_table.add_info_log(
                "CSV로 저장할 미리보기 결과가 없습니다."
            )
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self.page,
            "미리보기 결과 CSV 저장",
            "scan_preview_results.csv",
            "CSV Files (*.csv)",
        )

        if not file_path:
            return

        try:
            self._write_preview_rows_csv(file_path, rows)
        except Exception as error:
            self.page.log_table.add_info_log(
                f"미리보기 결과 CSV 저장 실패: {error}"
            )
            return

        self.page.log_table.add_info_log(
            f"미리보기 결과 CSV 저장 완료: {file_path}"
        )

    def _write_rows_csv(
        self,
        file_path: str | Path,
        rows: list[dict],
    ):
        fieldnames = [
            "time",
            "progress",
            "result",
            "artist_name",
            "pixiv_id",
            "artwork_count",
            "file_count",
            "update_status",
            "folder_path",
            "error_message",
        ]

        with open(
            file_path,
            "w",
            newline="",
            encoding="utf-8-sig",
        ) as csv_file:
            writer = csv.DictWriter(
                csv_file,
                fieldnames=fieldnames,
            )
            writer.writeheader()

            for row in rows:
                writer.writerow(
                    {
                        "time": row.get("time", "-"),
                        "progress": row.get("progress", "-"),
                        "result": row.get("result", "-"),
                        "artist_name": row.get("artist_name", "-"),
                        "pixiv_id": row.get("pixiv_id", "-"),
                        "artwork_count": row.get("artwork_count", "-"),
                        "file_count": row.get("file_count", "-"),
                        "update_status": row.get("update_status", "-"),
                        "folder_path": row.get("folder_path", "-"),
                        "error_message": row.get("error_message", "-"),
                    }
                )

    def _write_preview_rows_csv(
        self,
        file_path: str | Path,
        rows: list[dict],
    ):
        fieldnames = [
            "selected",
            "excluded",
            "preview_result",
            "artist_name",
            "pixiv_id",
            "artwork_count",
            "file_count",
            "folder_path",
            "message",
        ]

        with open(
            file_path,
            "w",
            newline="",
            encoding="utf-8-sig",
        ) as csv_file:
            writer = csv.DictWriter(
                csv_file,
                fieldnames=fieldnames,
            )
            writer.writeheader()

            for row in rows:
                writer.writerow(
                    {
                        "selected": row.get("selected", "0"),
                        "excluded": row.get("is_excluded", "0"),
                        "preview_result": row.get("preview_result", "-"),
                        "artist_name": row.get("artist_name", "-"),
                        "pixiv_id": row.get("pixiv_id", "-"),
                        "artwork_count": row.get("artwork_count", "-"),
                        "file_count": row.get("file_count", "-"),
                        "folder_path": row.get("folder_path", "-"),
                        "message": row.get("message", "-"),
                    }
                )

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

    def _load_json_setting(
        self,
        key: str,
    ):
        value = self.page.settings_service.get_setting(key)

        if not value:
            return None

        try:
            return json.loads(str(value))
        except json.JSONDecodeError:
            return None

    def _save_json_setting(
        self,
        key: str,
        value,
    ):
        self.page.settings_service.set_setting(
            key,
            json.dumps(
                value,
                ensure_ascii=False,
            ),
        )

    def _build_latest_compare_result(
        self,
        history: list[dict],
    ) -> dict | None:
        if len(history) < 2:
            return None

        latest = history[0]
        previous = history[1]

        return self._build_compare_result(
            latest=latest,
            previous=previous,
        )

    def _build_compare_result(
        self,
        latest: dict,
        previous: dict,
    ) -> dict:
        fields = [
            ("total", "대상"),
            ("created", "등록"),
            ("updated", "업데이트"),
            ("unchanged", "변경 없음"),
            ("failed", "실패"),
            ("total_file_count", "파일"),
            ("total_artwork_count", "작품"),
        ]

        items = []

        for key, label in fields:
            latest_value = self._safe_int(latest.get(key))
            previous_value = self._safe_int(previous.get(key))
            diff = latest_value - previous_value

            items.append(
                {
                    "key": key,
                    "label": label,
                    "latest": latest_value,
                    "previous": previous_value,
                    "diff": diff,
                }
            )

        return {
            "latest_finished_at": latest.get("finished_at_text", "-"),
            "previous_finished_at": previous.get("finished_at_text", "-"),
            "items": items,
        }

    def _safe_int(
        self,
        value,
    ) -> int:
        try:
            return int(value or 0)
        except (TypeError, ValueError):
            return 0
