from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices

from ..database_utils import get_database_path


class SettingsDatabaseActions:
    def refresh_database_info(self):
        try:
            database_info = self.database_info_service.get_database_info()
            program_info = self.database_info_service.get_program_info()
        except Exception as error:
            self.set_status(f"DB 정보 조회 실패: {error}", error=True)
            return

        self.page.database_section.update_database_info(database_info)
        self.page.app_info_section.update_program_info(program_info)

    def run_integrity_check(self):
        try:
            result = self.database_integrity_service.check_integrity()
        except Exception as error:
            self.set_status(f"무결성 검사 실패: {error}", error=True)
            return

        result_text = self._format_integrity_result(result)
        self.page.database_section.update_integrity_result(result_text)

        if result.get("ok"):
            self.set_status("무결성 검사 완료: 문제가 없습니다.")
            return

        self.set_status(
            f"무결성 검사 완료: {result.get('issue_count', 0)}건 발견",
            error=True,
        )

    def optimize_database(self):
        self.set_status("DB 최적화 중...")

        try:
            result = self.database_maintenance_service.optimize_database()
        except Exception as error:
            self.set_status(f"DB 최적화 실패: {error}", error=True)
            return

        result_text = (
            "DB 최적화 완료\n\n"
            f"최적화 전: {result.get('before_size_label')}\n"
            f"최적화 후: {result.get('after_size_label')}\n"
            f"절감 용량: {result.get('saved_size_label')}\n"
            f"소요 시간: {result.get('elapsed_seconds')}초"
        )

        self.page.database_section.update_integrity_result(result_text)
        self.refresh_database_info()
        self.set_status("DB 최적화가 완료되었습니다.")

    def open_db_folder(self):
        db_path = get_database_path()

        if not db_path.exists():
            self.set_status("DB 파일을 찾을 수 없습니다.", error=True)
            return

        QDesktopServices.openUrl(QUrl.fromLocalFile(str(db_path.parent)))

    def open_backup_folder(self):
        backup_dir = self.database_backup_service.BACKUP_DIR
        backup_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        QDesktopServices.openUrl(QUrl.fromLocalFile(str(backup_dir)))
