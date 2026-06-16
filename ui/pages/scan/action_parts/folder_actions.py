import subprocess
from pathlib import Path

from PySide6.QtWidgets import QFileDialog


class ScanFolderActions:
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

    def select_folder(self):
        folder_path = QFileDialog.getExistingDirectory(
            self.page,
            "스캔할 폴더 선택",
            self.page.folder_section.folder_path_input.text().strip(),
        )

        if not folder_path:
            return

        self.page.folder_section.folder_path_input.setText(folder_path)
        self.clear_resume_state()

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
