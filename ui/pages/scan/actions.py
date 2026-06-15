import csv
import json
import subprocess
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QThread
from PySide6.QtWidgets import QFileDialog

from .worker import ScanWorker


class ScanActions:
    SCAN_RESULT_DIR = Path("data") / "scan_results"
    LATEST_SCAN_JSON_PATH = SCAN_RESULT_DIR / "latest_scan.json"
    LATEST_SCAN_CSV_PATH = SCAN_RESULT_DIR / "latest_scan.csv"
    RECENT_HISTORY_LIMIT = 10

    def __init__(self, page):
        self.page = page

    def load_default_folder(self):
        folder_path = self.page.settings_service.get_setting(
            "pixiv_root_folder"
        )

        if not folder_path:
            folder_path = self.page.settings_service.get_setting(
                "last_scan_folder"
            )

        if folder_path:
            self.page.folder_section.folder_path_input.setText(folder_path)

        self.load_scan_history()

    def load_scan_history(self):
        last_scan_result = self._load_json_setting("last_scan_result")
        recent_scan_history = self._load_json_setting("recent_scan_history")

        if not isinstance(recent_scan_history, list):
            recent_scan_history = []

        self.page.progress_section.update_last_scan_info(last_scan_result)
        self.page.progress_section.update_recent_scan_history(
            recent_scan_history
        )

    def select_folder(self):
        folder_path = QFileDialog.getExistingDirectory(
            self.page,
            "스캔할 폴더 선택",
            self.page.folder_section.folder_path_input.text().strip(),
        )

        if not folder_path:
            return

        self.page.folder_section.folder_path_input.setText(folder_path)

    def start_preview(self):
        folder_path = self.page.folder_section.folder_path_input.text().strip()

        if not folder_path:
            self.page.log_table.add_info_log("오류: 먼저 폴더를 선택하세요.")
            return

        self.page.settings_service.set_setting(
            "last_scan_folder",
            folder_path,
        )

        self._start_worker(
            folder_path=folder_path,
            target_folder_paths=None,
            clear_log=True,
            preview_mode=True,
        )

    def start_scan(self):
        folder_path = self.page.folder_section.folder_path_input.text().strip()

        if not folder_path:
            self.page.log_table.add_info_log("오류: 먼저 폴더를 선택하세요.")
            return

        self.page.settings_service.set_setting(
            "last_scan_folder",
            folder_path,
        )

        self._start_worker(
            folder_path=folder_path,
            target_folder_paths=None,
            clear_log=True,
            preview_mode=False,
        )

    def start_selected_preview_items_scan(self):
        folder_paths = self.page.preview_table.get_selected_folder_paths()

        if not folder_paths:
            self.page.log_table.add_info_log("선택된 등록 대상이 없습니다.")
            return

        root_folder = self.page.folder_section.folder_path_input.text().strip()

        if not root_folder:
            root_folder = str(Path(folder_paths[0]).parent)

        self.page.log_table.add_info_log(
            f"선택 항목 등록 시작: {len(folder_paths)}개"
        )

        self._start_worker(
            folder_path=root_folder,
            target_folder_paths=folder_paths,
            clear_log=True,
            preview_mode=False,
        )

    def retry_failed_items(self):
        failed_rows = self.page.log_table.get_failed_rows()

        if not failed_rows:
            self.page.log_table.add_info_log("재시도할 실패 항목이 없습니다.")
            return

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
        )

    def clear_failed_items(self):
        self.page.log_table.clear_failed_rows()
        self.page.log_table.add_info_log("실패 목록을 초기화했습니다.")

    def export_failed_items_csv(self):
        failed_rows = self.page.log_table.get_failed_rows()

        if not failed_rows:
            self.page.log_table.add_info_log("CSV로 저장할 실패 항목이 없습니다.")
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

    def _start_worker(
        self,
        folder_path: str,
        target_folder_paths: list[str] | None,
        clear_log: bool,
        preview_mode: bool,
    ):
        if self.page.scan_thread is not None:
            self.page.log_table.add_info_log("이미 스캔이 진행 중입니다.")
            return

        self.set_scanning_state(True)
        self.page.progress_section.reset()
        self.load_scan_history()

        if clear_log:
            self.page.log_table.clear_log()

        if preview_mode:
            self.page.preview_table.clear_preview()
            self.page.log_table.add_info_log(f"스캔 미리보기 시작: {folder_path}")
        else:
            self.page.log_table.add_info_log(f"스캔 시작: {folder_path}")

        self.page.scan_thread = QThread()
        self.page.scan_worker = ScanWorker(
            folder_path,
            target_folder_paths=target_folder_paths,
            preview_mode=preview_mode,
        )
        self.page.scan_worker.moveToThread(self.page.scan_thread)

        self.page.scan_thread.started.connect(
            self.page.scan_worker.run
        )
        self.page.scan_worker.log_message_requested.connect(
            self.page.log_table.add_info_log
        )
        self.page.scan_worker.scan_result_requested.connect(
            self.page.log_table.add_log_row
        )
        self.page.scan_worker.preview_result_requested.connect(
            self.page.preview_table.set_preview_rows
        )
        self.page.scan_worker.preview_summary_updated.connect(
            self.page.progress_section.update_summary
        )
        self.page.scan_worker.progress_updated.connect(
            self.page.progress_section.update_progress
        )
        self.page.scan_worker.current_folder_changed.connect(
            self.page.progress_section.update_current_folder
        )
        self.page.scan_worker.target_count_changed.connect(
            self.page.progress_section.update_target_count
        )
        self.page.scan_worker.summary_updated.connect(
            self.page.progress_section.update_summary
        )
        self.page.scan_worker.statistics_updated.connect(
            self.page.progress_section.update_statistics
        )
        self.page.scan_worker.runtime_info_updated.connect(
            self.page.progress_section.update_runtime_info
        )
        self.page.scan_worker.failed.connect(
            self.handle_scan_failed
        )
        self.page.scan_worker.finished.connect(
            self.handle_scan_finished
        )

        self.page.scan_worker.finished.connect(
            self.page.scan_thread.quit
        )
        self.page.scan_worker.failed.connect(
            self.page.scan_thread.quit
        )
        self.page.scan_thread.finished.connect(
            self.cleanup_scan_thread
        )

        self.page.scan_thread.start()

    def handle_scan_finished(
        self,
        result: dict,
    ):
        if self.page.scan_worker is not None and self.page.scan_worker.preview_mode:
            self.set_scanning_state(False)
            return

        self._save_scan_result(result)
        self.load_scan_history()
        self.set_scanning_state(False)

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

    def handle_scan_failed(self, error_message: str):
        self.page.log_table.add_log_row(
            {
                "time": datetime.now().strftime("%H:%M:%S"),
                "progress": "-",
                "result": "실패",
                "artist_id": None,
                "artist_name": "스캔 작업 오류",
                "pixiv_id": "-",
                "artwork_count": "-",
                "file_count": "-",
                "update_status": "error",
                "folder_path": (
                    self.page.folder_section.folder_path_input.text().strip()
                ),
                "error_message": error_message,
            }
        )
        self.set_scanning_state(False)

    def cleanup_scan_thread(self):
        if self.page.scan_worker is not None:
            self.page.scan_worker.deleteLater()
            self.page.scan_worker = None

        if self.page.scan_thread is not None:
            self.page.scan_thread.deleteLater()
            self.page.scan_thread = None

    def set_scanning_state(self, is_scanning: bool):
        self.page.folder_section.scan_button.setEnabled(not is_scanning)
        self.page.folder_section.preview_button.setEnabled(not is_scanning)
        self.page.folder_section.folder_select_button.setEnabled(
            not is_scanning
        )

        self.page.clear_log_button.setEnabled(not is_scanning)
        self.page.retry_failed_button.setEnabled(not is_scanning)
        self.page.clear_failed_button.setEnabled(not is_scanning)
        self.page.export_failed_csv_button.setEnabled(not is_scanning)
        self.page.export_all_csv_button.setEnabled(not is_scanning)
        self.page.preview_scan_selected_button.setEnabled(not is_scanning)
        self.page.preview_select_all_button.setEnabled(not is_scanning)
        self.page.preview_clear_selection_button.setEnabled(not is_scanning)
        self.page.preview_exclude_error_button.setEnabled(not is_scanning)

        if is_scanning:
            self.page.folder_section.scan_button.setText("스캔 중...")
        else:
            self.page.folder_section.scan_button.setText("스캔 및 등록")

    def apply_result_filter(self):
        result_filter = self.page.result_filter_combo.currentText()
        self.page.log_table.set_result_filter(result_filter)

    def apply_error_only_filter(self):
        self.page.log_table.set_error_only(
            self.page.error_only_checkbox.isChecked()
        )

    def clear_scan_results(self):
        self.page.log_table.clear_log()
        self.page.preview_table.clear_preview()
        self.page.progress_section.reset()
        self.load_scan_history()

    def open_artist_detail(self, artist_id: int):
        self.page.artist_detail_requested.emit(artist_id)

    def open_folder(self, folder_path: str):
        folder_path = str(folder_path or "").strip()

        if not folder_path:
            return

        path = Path(folder_path)

        if not path.exists():
            self.page.log_table.add_info_log(
                f"폴더를 찾을 수 없습니다: {folder_path}"
            )
            return

        try:
            subprocess.Popen(
                f'explorer.exe "{path}"',
                shell=True,
            )
        except Exception as error:
            self.page.log_table.add_info_log(
                f"폴더를 열지 못했습니다: {error}"
            )
