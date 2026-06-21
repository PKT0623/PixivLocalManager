class SettingsLoadActions:
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
            self.page.pixiv_section.session_status_label.setText(
                "세션 상태: 미확인"
            )

        self._load_pixiv_request_settings()
        self._load_update_check_request_settings()
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
        self.page.pixiv_section.session_status_label.setText(
            "세션 상태: 미확인"
        )

    def _load_pixiv_request_settings(self):
        section = self.page.pixiv_manager_request_section

        section.request_interval_ms_input.setText(
            str(
                self.page.settings_service.get_int_setting(
                    "pixiv_request_interval_ms",
                    2000,
                )
            )
        )
        section.batch_size_input.setText(
            str(
                self.page.settings_service.get_int_setting(
                    "pixiv_batch_size",
                    1000,
                )
            )
        )
        section.batch_rest_ms_input.setText(
            str(
                self.page.settings_service.get_int_setting(
                    "pixiv_batch_rest_ms",
                    300000,
                )
            )
        )
        section.retry_count_input.setText(
            str(
                self.page.settings_service.get_int_setting(
                    "pixiv_retry_count",
                    3,
                )
            )
        )

    def _load_update_check_request_settings(self):
        section = self.page.update_check_request_section

        section.request_interval_ms_input.setText(
            str(
                self.page.settings_service.get_int_setting(
                    "update_check_request_interval_ms",
                    1000,
                )
            )
        )
        section.batch_size_input.setText(
            str(
                self.page.settings_service.get_int_setting(
                    "update_check_batch_size",
                    20,
                )
            )
        )
        section.batch_rest_ms_input.setText(
            str(
                self.page.settings_service.get_int_setting(
                    "update_check_batch_rest_ms",
                    180000,
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
