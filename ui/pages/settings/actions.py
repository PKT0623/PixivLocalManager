from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QFileDialog

from .database_utils import (
    create_database_backup,
    create_restore_safety_backup,
    export_artists_to_csv,
    get_database_path,
    is_valid_sqlite_database,
    restore_database,
)


class SettingsActions:
    def __init__(self, page):
        self.page = page

    def load_settings(self):
        pixiv_root_folder = self.page.settings_service.get_setting(
            "pixiv_root_folder"
        )

        if pixiv_root_folder:
            self.page.folder_section.pixiv_root_input.setText(pixiv_root_folder)

        phpsessid = self.page.settings_service.get_setting("pixiv_phpsessid")

        if phpsessid:
            self.page.pixiv_section.phpsessid_input.setText(phpsessid)
            self.page.pixiv_section.phpsessid_status_label.setText(
                f"저장됨: {self.mask_secret(phpsessid)}"
            )

        db_path = get_database_path()
        self.page.database_section.db_path_input.setText(str(db_path))

    def select_pixiv_root_folder(self):
        folder_path = QFileDialog.getExistingDirectory(
            self.page,
            "기본 Pixiv 폴더 선택",
            self.page.folder_section.pixiv_root_input.text().strip(),
        )

        if not folder_path:
            return

        self.page.folder_section.pixiv_root_input.setText(folder_path)
        self.set_status("기본 Pixiv 폴더를 선택했습니다. 저장 버튼을 눌러 반영하세요.")

    def save_pixiv_root_folder(self):
        folder_path = self.page.folder_section.pixiv_root_input.text().strip()

        if not folder_path:
            self.set_status("저장할 Pixiv 폴더가 없습니다.", error=True)
            return

        try:
            self.page.settings_service.set_setting(
                "pixiv_root_folder",
                folder_path,
            )
        except Exception as error:
            self.set_status(f"기본 Pixiv 폴더 저장 실패: {error}", error=True)
            return

        self.set_status("기본 Pixiv 폴더가 저장되었습니다.")

    def save_phpsessid(self):
        phpsessid = self.page.pixiv_section.phpsessid_input.text().strip()

        if not phpsessid:
            self.set_status("저장할 PHPSESSID가 없습니다.", error=True)
            return

        try:
            self.page.settings_service.set_setting(
                "pixiv_phpsessid",
                phpsessid,
            )
        except Exception as error:
            self.set_status(f"PHPSESSID 저장 실패: {error}", error=True)
            return

        self.page.pixiv_section.phpsessid_status_label.setText(
            f"저장됨: {self.mask_secret(phpsessid)}"
        )
        self.set_status("Pixiv PHPSESSID가 저장되었습니다.")

    def open_db_folder(self):
        db_path = get_database_path()

        if not db_path.exists():
            self.set_status("DB 파일을 찾을 수 없습니다.", error=True)
            return

        QDesktopServices.openUrl(QUrl.fromLocalFile(str(db_path.parent)))

    def backup_database(self):
        db_path = get_database_path()

        if not db_path.exists():
            self.set_status("백업할 DB 파일을 찾을 수 없습니다.", error=True)
            return

        if not is_valid_sqlite_database(db_path):
            self.set_status(
                "DB 백업 실패: 현재 DB 파일이 유효한 SQLite DB가 아닙니다.",
                error=True,
            )
            return

        backup_folder = QFileDialog.getExistingDirectory(
            self.page,
            "DB 백업 폴더 선택",
            str(db_path.parent),
        )

        if not backup_folder:
            return

        try:
            backup_path = create_database_backup(db_path, backup_folder)
        except OSError as error:
            self.set_status(f"DB 백업 실패: {error}", error=True)
            return

        self.set_status(f"DB 백업 완료: {backup_path}")

    def restore_database(self):
        db_path = get_database_path()

        restore_file, _ = QFileDialog.getOpenFileName(
            self.page,
            "복원할 DB 파일 선택",
            str(db_path.parent),
            "SQLite DB (*.db);;All Files (*)",
        )

        if not restore_file:
            return

        restore_path = Path(restore_file)

        if not is_valid_sqlite_database(restore_path):
            self.set_status(
                "DB 복원 실패: 유효한 SQLite DB 파일이 아닙니다.",
                error=True,
            )
            return

        try:
            if db_path.exists() and is_valid_sqlite_database(db_path):
                create_restore_safety_backup(db_path)

            restore_database(restore_path, db_path)
        except OSError as error:
            self.set_status(f"DB 복원 실패: {error}", error=True)
            return

        self.set_status("DB 복원이 완료되었습니다. 프로그램을 재시작하세요.")

    def export_artists_csv(self):
        export_file, _ = QFileDialog.getSaveFileName(
            self.page,
            "작가 목록 CSV 내보내기",
            "artists.csv",
            "CSV Files (*.csv);;All Files (*)",
        )

        if not export_file:
            return

        if not export_file.lower().endswith(".csv"):
            export_file += ".csv"

        artists = self.page.artist_service.get_all_artists()

        try:
            export_artists_to_csv(export_file, artists)
        except OSError as error:
            self.set_status(f"CSV 내보내기 실패: {error}", error=True)
            return

        self.set_status(f"CSV 내보내기 완료: {export_file}")

    def mask_secret(self, value: str) -> str:
        if len(value) <= 8:
            return "*" * len(value)

        return f"{value[:4]}{'*' * 8}{value[-4:]}"

    def set_status(self, message: str, error: bool = False):
        self.page.status_label.setText(message)

        if error:
            self.page.status_label.setStyleSheet("color: #dc3545;")
            return

        self.page.status_label.setStyleSheet("color: #198754;")
