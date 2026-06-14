from datetime import datetime

from PySide6.QtCore import QThread
from PySide6.QtWidgets import QFileDialog

from .worker import ScanWorker


class ScanActions:
    def __init__(self, page):
        self.page = page

    def load_default_folder(self):
        folder_path = self.page.settings_service.get_setting(
            "pixiv_root_folder"
        )

        if not folder_path:
            return

        self.page.folder_section.folder_path_input.setText(folder_path)
        self.page.log_table.add_info_log(
            f"기본 Pixiv 폴더 불러옴: {folder_path}"
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
        self.page.log_table.add_info_log(f"폴더 선택: {folder_path}")

    def start_scan(self):
        folder_path = self.page.folder_section.folder_path_input.text().strip()

        if not folder_path:
            self.page.log_table.add_info_log("오류: 먼저 폴더를 선택하세요.")
            return

        if self.page.scan_thread is not None:
            self.page.log_table.add_info_log("이미 스캔이 진행 중입니다.")
            return

        self.set_scanning_state(True)
        self.page.progress_section.reset()

        self.page.log_table.add_info_log("스캔 작업을 시작합니다.")
        self.page.log_table.add_info_log(f"대상 폴더: {folder_path}")
        self.page.log_table.add_info_log("탐색 깊이: 최대 3단계")

        self.page.scan_thread = QThread()
        self.page.scan_worker = ScanWorker(folder_path)
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
        self.page.scan_worker.progress_updated.connect(
            self.page.progress_section.update_progress
        )
        self.page.scan_worker.current_folder_changed.connect(
            self.page.progress_section.update_current_folder
        )
        self.page.scan_worker.target_count_changed.connect(
            self.page.progress_section.update_target_count
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

    def handle_scan_finished(self):
        self.page.log_table.add_info_log("스캔 작업이 완료되었습니다.")
        self.set_scanning_state(False)

    def handle_scan_failed(self, error_message: str):
        self.page.log_table.add_log_row(
            {
                "time": datetime.now().strftime("%H:%M:%S"),
                "progress": "-",
                "result": "실패",
                "artist_name": error_message,
                "pixiv_id": "-",
                "artwork_count": "-",
                "file_count": "-",
                "update_status": "error",
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
        self.page.folder_section.folder_select_button.setEnabled(not is_scanning)

        if is_scanning:
            self.page.folder_section.scan_button.setText("스캔 중...")
        else:
            self.page.folder_section.scan_button.setText("스캔 및 등록")
