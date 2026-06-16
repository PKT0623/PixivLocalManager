import json
from pathlib import Path
from typing import Any, Dict


class BackupJsonUtils:

    def load_json_file(
        self,
        file_path: str,
    ) -> Dict[str, Any]:
        with open(
            file_path,
            "r",
            encoding="utf-8",
        ) as f:
            data = json.load(f)

        if not isinstance(data, dict):
            raise ValueError("백업 파일 형식이 올바르지 않습니다.")

        return data

    def save_json_file(
        self,
        file_path: str | Path,
        data: Dict[str, Any],
    ) -> str:
        with open(
            file_path,
            "w",
            encoding="utf-8",
        ) as f:
            json.dump(
                data,
                f,
                ensure_ascii=False,
                indent=4,
                default=self.json_default,
            )

        return str(file_path)

    def delete_file_if_exists(
        self,
        file_path: str,
    ) -> None:
        path = Path(file_path)

        if not path.exists():
            return

        if not path.is_file():
            return

        path.unlink()

    def get_setting_value(
        self,
        setting,
        key: str,
    ):
        if isinstance(setting, dict):
            return setting.get(key)

        return getattr(setting, key, None)

    def json_default(self, value):
        if hasattr(value, "__dict__"):
            return value.__dict__

        return str(value)
