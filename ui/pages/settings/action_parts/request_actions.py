class SettingsRequestActions:
    def save_pixiv_request_settings(self):
        section = self.page.pixiv_manager_request_section

        request_interval_ms = self._read_int(
            section.request_interval_ms_input.text(),
            2000,
        )
        batch_size = self._read_int(
            section.batch_size_input.text(),
            1000,
        )
        batch_rest_ms = self._read_int(
            section.batch_rest_ms_input.text(),
            300000,
        )
        retry_count = self._read_int(
            section.retry_count_input.text(),
            3,
        )

        request_interval_ms = max(2000, request_interval_ms)
        batch_size = max(1, batch_size)
        batch_rest_ms = max(0, batch_rest_ms)
        retry_count = max(0, retry_count)

        try:
            self.page.settings_service.set_setting(
                "pixiv_request_interval_ms",
                request_interval_ms,
            )
            self.page.settings_service.set_setting(
                "pixiv_batch_size",
                batch_size,
            )
            self.page.settings_service.set_setting(
                "pixiv_batch_rest_ms",
                batch_rest_ms,
            )
            self.page.settings_service.set_setting(
                "pixiv_retry_count",
                retry_count,
            )
        except Exception as error:
            self.set_status(f"Pixiv 관리 요청 저장 실패: {error}", error=True)
            return

        self._load_pixiv_request_settings()
        self.set_status("Pixiv 관리 요청 설정이 저장되었습니다.")

    def save_update_check_request_settings(self):
        section = self.page.update_check_request_section

        request_interval_ms = self._read_int(
            section.request_interval_ms_input.text(),
            1000,
        )
        batch_size = self._read_int(
            section.batch_size_input.text(),
            20,
        )
        batch_rest_ms = self._read_int(
            section.batch_rest_ms_input.text(),
            180000,
        )

        request_interval_ms = max(0, request_interval_ms)
        batch_size = max(1, batch_size)
        batch_rest_ms = max(0, batch_rest_ms)

        try:
            self.page.settings_service.set_setting(
                "update_check_request_interval_ms",
                request_interval_ms,
            )
            self.page.settings_service.set_setting(
                "update_check_batch_size",
                batch_size,
            )
            self.page.settings_service.set_setting(
                "update_check_batch_rest_ms",
                batch_rest_ms,
            )
        except Exception as error:
            self.set_status(f"업데이트 확인 요청 저장 실패: {error}", error=True)
            return

        self._load_update_check_request_settings()
        self.set_status("업데이트 확인 요청 설정이 저장되었습니다.")
