from ..worker_config import (
    DEFAULT_UPDATE_CHECK_BATCH_REST_MS,
    DEFAULT_UPDATE_CHECK_BATCH_SIZE,
    DEFAULT_UPDATE_CHECK_REQUEST_INTERVAL_MS,
)


class UpdateCheckSettingsMixin:
    def load_request_settings(self):
        self.request_interval_ms_input.setText(
            str(
                self.settings_service.get_int_setting(
                    "update_check_request_interval_ms",
                    DEFAULT_UPDATE_CHECK_REQUEST_INTERVAL_MS,
                )
            )
        )
        self.batch_size_input.setText(
            str(
                self.settings_service.get_int_setting(
                    "update_check_batch_size",
                    DEFAULT_UPDATE_CHECK_BATCH_SIZE,
                )
            )
        )
        self.batch_rest_ms_input.setText(
            str(
                self.settings_service.get_int_setting(
                    "update_check_batch_rest_ms",
                    DEFAULT_UPDATE_CHECK_BATCH_REST_MS,
                )
            )
        )

    def get_request_interval_ms(self) -> int:
        return self._read_int(
            self.request_interval_ms_input.text(),
            DEFAULT_UPDATE_CHECK_REQUEST_INTERVAL_MS,
        )

    def get_batch_size(self) -> int:
        return self._read_int(
            self.batch_size_input.text(),
            DEFAULT_UPDATE_CHECK_BATCH_SIZE,
        )

    def get_batch_rest_ms(self) -> int:
        return self._read_int(
            self.batch_rest_ms_input.text(),
            DEFAULT_UPDATE_CHECK_BATCH_REST_MS,
        )

    def _read_int(
        self,
        value: str,
        default: int,
    ) -> int:
        try:
            return max(0, int(value))
        except (TypeError, ValueError):
            return default
