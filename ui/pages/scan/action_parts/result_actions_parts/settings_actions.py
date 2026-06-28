import json


class ScanResultSettingsActionsMixin:
    def _load_json_setting(
        self,
        key: str,
    ):
        value = self.page.settings_service.get_setting(key)

        if not value:
            return None

        try:
            return json.loads(str(value))
        except json.JSONDecodeError:
            return None

    def _save_json_setting(
        self,
        key: str,
        value,
    ):
        self.page.settings_service.set_setting(
            key,
            json.dumps(
                value,
                ensure_ascii=False,
            ),
        )
