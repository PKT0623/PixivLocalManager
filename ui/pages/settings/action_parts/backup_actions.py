from datetime import datetime
from pathlib import Path

from PySide6.QtWidgets import QFileDialog

from ..database_utils import export_artists_to_csv


class SettingsBackupActions:
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
