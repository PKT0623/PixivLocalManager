from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QFileDialog

from app.services.backup import DatabaseBackupService
from app.services.database_info_service import DatabaseInfoService
from app.services.database_integrity_service import DatabaseIntegrityService
from app.services.database_maintenance_service import (
    DatabaseMaintenanceService,
)
from app.services.pixiv_update_service import PixivUpdateService
from app.services.settings_backup_service import SettingsBackupService

from .database_utils import (
    export_artists_to_csv,
    get_database_path,
)


class SettingsActions:
    def __init__(self, page):
        self.page = page
        self.database_backup_service = DatabaseBackupService()
        self.database_info_service = DatabaseInfoService()
        self.database_integrity_service = DatabaseIntegrityService()
        self.database_maintenance_service = DatabaseMaintenanceService()
        self.settings_backup_service = SettingsBackupService()

    def load_settings(self):
        self._clear_setting_inputs()

        pixiv_root_folder = self.page.settings_service.get_setting(
            "pixiv_root_folder"
        )

        if pixiv_root_folder:
            self.page.folder_section.pixiv_root_input.setText(
                pixiv_root_folder
            )

        phpsessid = self.page.settings_service.get_setting("pixiv_phpsessid")

        if phpsessid:
            self.page.pixiv_section.phpsessid_input.setText(phpsessid)
            self.page.pixiv_section.phpsessid_status_label.setText(
                f"저장됨: {self.mask_secret(phpsessid)}"
            )

        self._load_pixiv_request_settings()
        self._load_backup_settings()
        self.refresh_database_info()
        self.refresh_backup_list()
        self.refresh_environment_info()

    def _clear_setting_inputs(self):
        self.page.folder_section.pixiv_root_input.clear()
        self.page.pixiv_section.phpsessid_input.clear()
        self.page.pixiv_section.phpsessid_status_label.setText(
            "저장된 PHPSESSID 없음"
        )

    def _load_pixiv_request_settings(self):
        section = self.page.pixiv_section

        section.request_interval_min_input.setText(
            str(
                self.page.settings_service.get_int_setting(
                    "pixiv_request_interval_min",
                    3,
                )
            )
        )
        section.request_interval_max_input.setText(
            str(
                self.page.settings_service.get_int_setting(
                    "pixiv_request_interval_max",
                    6,
                )
            )
        )
        section.retry_count_input.setText(
            str(
                self.page.settings_service.get_int_setting(
                    "pixiv_retry_count",
                    2,
                )
            )
        )
        section.retry_interval_input.setText(
            str(
                self.page.settings_service.get_int_setting(
                    "pixiv_retry_interval",
                    5,
                )
            )
        )

    def _load_backup_settings(self):
        section = self.page.database_section

        section.auto_backup_enabled_checkbox.setChecked(
            self.database_backup_service.is_auto_backup_enabled()
        )
        section.backup_interval_input.setValue(
            self.database_backup_service.get_auto_backup_interval_days()
        )
        section.backup_keep_count_input.setValue(
            self.database_backup_service.get_auto_backup_keep_count()
        )

    def refresh_environment_info(self):
        width = self.page.settings_service.get_setting("window_width")
        height = self.page.settings_service.get_setting("window_height")
        x = self.page.settings_service.get_setting("window_x")
        y = self.page.settings_service.get_setting("window_y")

        window_size = "-"

        if width and height:
            window_size = f"{width} x {height}"

        window_position = "-"

        if x and y:
            window_position = f"X: {x}, Y: {y}"

        info = {
            "window_size": window_size,
            "window_position": window_position,
            "last_backup_folder": self._get_folder_label(
                "last_settings_backup_folder"
            ),
            "last_restore_folder": self._get_folder_label(
                "last_settings_restore_folder"
            ),
            "last_export_folder": self._get_folder_label(
                "last_export_folder"
            ),
        }

        self.page.settings_management_section.update_environment_info(info)

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

    def backup_settings(self):
        backup_dir = self._get_initial_folder(
            key="last_settings_backup_folder",
            fallback=self.settings_backup_service.get_default_backup_dir(),
        )
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_path = str(
            Path(backup_dir) / f"settings_backup_{timestamp}.json"
        )

        backup_file, _ = QFileDialog.getSaveFileName(
            self.page,
            "설정 백업 파일 저장",
            default_path,
            "JSON Files (*.json);;All Files (*)",
        )

        if not backup_file:
            return

        if not backup_file.lower().endswith(".json"):
            backup_file += ".json"

        try:
            backup_path = self.settings_backup_service.export_settings(
                backup_file
            )
            self._save_last_folder(
                "last_settings_backup_folder",
                backup_path,
            )
        except Exception as error:
            self.set_status(f"설정 백업 실패: {error}", error=True)
            return

        self.refresh_environment_info()
        self.set_status(f"설정 백업 완료: {backup_path}")

    def restore_settings(self):
        restore_dir = self._get_initial_folder(
            key="last_settings_restore_folder",
            fallback=self.settings_backup_service.get_default_backup_dir(),
        )

        restore_file, _ = QFileDialog.getOpenFileName(
            self.page,
            "복원할 설정 백업 파일 선택",
            str(restore_dir),
            "JSON Files (*.json);;All Files (*)",
        )

        if not restore_file:
            return

        try:
            result = self.settings_backup_service.import_settings(
                restore_file
            )
            self._save_last_folder(
                "last_settings_restore_folder",
                restore_file,
            )
        except Exception as error:
            self.set_status(f"설정 복원 실패: {error}", error=True)
            return

        self.load_settings()
        self.set_status(
            "설정 복원 완료: "
            f"{result.get('imported_count', 0)}개 복원, "
            f"{result.get('skipped_count', 0)}개 건너뜀"
        )

    def reset_settings(self):
        try:
            self.page.settings_service.reset_to_default()
        except Exception as error:
            self.set_status(f"설정 초기화 실패: {error}", error=True)
            return

        self.load_settings()
        self.set_status("설정을 기본값으로 초기화했습니다.")

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

        self.refresh_environment_info()
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

    def test_phpsessid(self):
        phpsessid = self.page.pixiv_section.phpsessid_input.text().strip()

        if not phpsessid:
            phpsessid = self.page.settings_service.get_setting(
                "pixiv_phpsessid"
            )

        if not phpsessid:
            self.set_status("테스트할 PHPSESSID가 없습니다.", error=True)
            return

        self.page.pixiv_section.test_phpsessid_button.setEnabled(False)
        self.set_status("PHPSESSID 테스트 중...")

        try:
            pixiv_service = PixivUpdateService.from_settings(
                self.page.settings_service
            )
            result = pixiv_service.test_phpsessid(phpsessid)
        except Exception as error:
            self.set_status(f"PHPSESSID 테스트 실패: {error}", error=True)
            self.page.pixiv_section.test_phpsessid_button.setEnabled(True)
            return

        self.page.pixiv_section.test_phpsessid_button.setEnabled(True)

        if result.get("success"):
            self.set_status("PHPSESSID가 유효합니다.")
            return

        self.set_status(
            f"PHPSESSID 테스트 실패: {result.get('message')}",
            error=True,
        )

    def save_pixiv_request_settings(self):
        section = self.page.pixiv_section

        min_interval = self._read_int(
            section.request_interval_min_input.text(),
            3,
        )
        max_interval = self._read_int(
            section.request_interval_max_input.text(),
            6,
        )
        retry_count = self._read_int(
            section.retry_count_input.text(),
            2,
        )
        retry_interval = self._read_int(
            section.retry_interval_input.text(),
            5,
        )

        if max_interval < min_interval:
            max_interval = min_interval

        try:
            self.page.settings_service.set_setting(
                "pixiv_request_interval_min",
                min_interval,
            )
            self.page.settings_service.set_setting(
                "pixiv_request_interval_max",
                max_interval,
            )
            self.page.settings_service.set_setting(
                "pixiv_retry_count",
                retry_count,
            )
            self.page.settings_service.set_setting(
                "pixiv_retry_interval",
                retry_interval,
            )
        except Exception as error:
            self.set_status(f"요청 설정 저장 실패: {error}", error=True)
            return

        self._load_pixiv_request_settings()
        self.set_status("Pixiv 요청 설정이 저장되었습니다.")

    def save_backup_settings(self):
        section = self.page.database_section

        try:
            self.database_backup_service.save_auto_backup_settings(
                enabled=section.auto_backup_enabled_checkbox.isChecked(),
                interval_days=section.backup_interval_input.value(),
                keep_count=section.backup_keep_count_input.value(),
            )
            deleted_paths = self.database_backup_service.prune_old_backups()
        except Exception as error:
            self.set_status(f"백업 설정 저장 실패: {error}", error=True)
            return

        self.refresh_backup_list()

        if deleted_paths:
            self.set_status(
                f"백업 설정 저장 완료. 초과 백업 {len(deleted_paths)}개를 정리했습니다."
            )
            return

        self.set_status("백업 설정이 저장되었습니다.")

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

    def backup_database(self):
        try:
            backup_path = self.database_backup_service.create_database_backup(
                backup_type="manual",
            )
            deleted_paths = self.database_backup_service.prune_old_backups()
        except Exception as error:
            self.set_status(f"DB 백업 실패: {error}", error=True)
            return

        self.refresh_backup_list()
        self.refresh_database_info()

        if deleted_paths:
            self.set_status(
                f"DB 백업 완료: {backup_path} / 초과 백업 {len(deleted_paths)}개 정리"
            )
            return

        self.set_status(f"DB 백업 완료: {backup_path}")

    def restore_database(self):
        backup_path = self.page.database_section.get_selected_backup_path()

        if not backup_path:
            self.set_status("복원할 백업을 선택하세요.", error=True)
            return

        try:
            self.database_backup_service.restore_database_backup(backup_path)
        except Exception as error:
            self.set_status(f"DB 복원 실패: {error}", error=True)
            return

        self.refresh_backup_list()
        self.refresh_database_info()
        self.set_status("DB 복원이 완료되었습니다. 프로그램을 재시작하세요.")

    def delete_selected_backup(self):
        backup_path = self.page.database_section.get_selected_backup_path()

        if not backup_path:
            self.set_status("삭제할 백업을 선택하세요.", error=True)
            return

        try:
            self.database_backup_service.delete_database_backup(backup_path)
        except Exception as error:
            self.set_status(f"백업 삭제 실패: {error}", error=True)
            return

        self.refresh_backup_list()
        self.refresh_database_info()
        self.set_status("선택한 백업을 삭제했습니다.")

    def refresh_backup_list(self):
        try:
            backups = self.database_backup_service.list_database_backups()
        except Exception as error:
            self.set_status(f"백업 목록 조회 실패: {error}", error=True)
            return

        self.page.database_section.update_backup_table(backups)
        self._update_backup_info_label(backups)

    def _update_backup_info_label(
        self,
        backups: list,
    ):
        last_backup_at = self.database_backup_service.get_last_backup_at_label()
        total_size = self.database_backup_service.get_backup_total_size_label()

        self.page.database_section.backup_info_label.setText(
            f"최근 백업: {last_backup_at} / "
            f"백업 수: {len(backups)}개 / "
            f"총 백업 용량: {total_size}"
        )

    def export_artists_csv(self):
        export_dir = self._get_initial_folder(
            key="last_export_folder",
            fallback=Path.cwd(),
        )

        export_file, _ = QFileDialog.getSaveFileName(
            self.page,
            "작가 목록 CSV 내보내기",
            str(Path(export_dir) / "artists.csv"),
            "CSV Files (*.csv);;All Files (*)",
        )

        if not export_file:
            return

        if not export_file.lower().endswith(".csv"):
            export_file += ".csv"

        artists = self.page.artist_service.get_all_artists()

        try:
            export_artists_to_csv(export_file, artists)
            self._save_last_folder(
                "last_export_folder",
                export_file,
            )
        except OSError as error:
            self.set_status(f"CSV 내보내기 실패: {error}", error=True)
            return

        self.refresh_environment_info()
        self.set_status(f"CSV 내보내기 완료: {export_file}")

    def mask_secret(self, value: str) -> str:
        if len(value) <= 8:
            return "*" * len(value)

        return f"{value[:4]}{'*' * 8}{value[-4:]}"

    def _format_integrity_result(
        self,
        result: dict,
    ) -> str:
        if result.get("ok"):
            return "무결성 검사 완료\n\n문제가 발견되지 않았습니다."

        lines = [
            "무결성 검사 완료",
            "",
            f"발견된 문제: {result.get('issue_count', 0)}건",
            "",
        ]

        grouped_issues = {}

        for issue in result.get("issues", []):
            issue_type = issue.get("type", "기타")
            grouped_issues.setdefault(issue_type, []).append(issue)

        for issue_type, issues in grouped_issues.items():
            lines.append(f"[{issue_type}]")

            for issue in issues:
                lines.append(
                    "- "
                    f"{issue.get('artist_name', '-')} "
                    f"(ID: {issue.get('artist_id', '-')}, "
                    f"Pixiv: {issue.get('pixiv_id', '-')})"
                )
                lines.append(f"  {issue.get('detail', '')}")

            lines.append("")

        return "\n".join(lines)

    def _get_initial_folder(
        self,
        key: str,
        fallback,
    ) -> Path:
        saved_folder = self.page.settings_service.get_setting(key)

        if saved_folder and Path(saved_folder).exists():
            return Path(saved_folder)

        return Path(fallback)

    def _save_last_folder(
        self,
        key: str,
        file_path: str,
    ):
        folder_path = Path(file_path).parent

        self.page.settings_service.set_setting(
            key,
            str(folder_path),
        )

    def _get_folder_label(
        self,
        key: str,
    ) -> str:
        folder = self.page.settings_service.get_setting(key)

        if not folder:
            return "-"

        return str(folder)

    def _read_int(
        self,
        value: str,
        default: int,
    ) -> int:
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    def set_status(self, message: str, error: bool = False):
        self.page.status_label.setText(message)

        if error:
            self.page.status_label.setStyleSheet("color: #dc3545;")
            return

        self.page.status_label.setStyleSheet("color: #198754;")
