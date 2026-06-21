from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices


class SettingsLogActions:
    def refresh_log_list(self):
        logs = self.log_management_service.list_log_files()
        self.page.log_section.update_log_table(logs)

        if not logs:
            self.page.log_section.set_log_content(
                "조회 가능한 로그 파일이 없습니다."
            )
            self.set_status("로그 목록 조회 완료: 0개")
            return

        self.set_status(f"로그 목록 조회 완료: {len(logs)}개")

    def load_selected_log(self):
        log_path = self.page.log_section.get_selected_log_path()

        if not log_path:
            return

        content = self.log_management_service.read_log_file(log_path)
        self.page.log_section.set_log_content(content)

    def delete_selected_log(self):
        log_path = self.page.log_section.get_selected_log_path()

        if not log_path:
            self.set_status("삭제할 로그를 선택하세요.", error=True)
            return

        if not self.log_management_service.delete_log_file(log_path):
            self.set_status("로그 삭제 실패", error=True)
            return

        self.page.log_section.clear_log_content()
        self.refresh_log_list()
        self.set_status("선택 로그가 삭제되었습니다.")

    def delete_all_logs(self):
        deleted_count = self.log_management_service.delete_all_logs()
        self.page.log_section.clear_log_content()
        self.refresh_log_list()
        self.set_status(f"로그 {deleted_count}개가 삭제되었습니다.")

    def open_log_folder(self):
        log_dir = self.log_management_service.ensure_log_dir()
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(log_dir)))

