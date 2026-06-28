from typing import Any

from .constants import (
    BOOL_SETTING_KEYS,
    DEFAULT_SCAN_IMAGE_EXTENSIONS,
    INT_SETTING_RULES,
    SCAN_IMAGE_EXTENSIONS_KEY,
)


class SettingsValueParserMixin:
    INT_SETTING_RULES = INT_SETTING_RULES
    BOOL_SETTING_KEYS = BOOL_SETTING_KEYS

    def get_int_setting(
        self,
        key: str,
        default: int,
    ) -> int:
        value = self.get_setting(key)
        rule = self.INT_SETTING_RULES.get(key)

        if value is None or value == "":
            return default

        try:
            parsed_value = int(value)
        except (TypeError, ValueError):
            return default

        if rule is None:
            return parsed_value

        return self.clamp_int(
            value=parsed_value,
            minimum=rule["minimum"],
            maximum=rule["maximum"],
        )

    def get_bool_setting(
        self,
        key: str,
        default: bool = False,
    ) -> bool:
        value = self.get_setting(key)

        if value is None:
            return default

        normalized_value = str(value).strip().lower()

        if normalized_value in {
            "1",
            "true",
            "yes",
            "on",
        }:
            return True

        if normalized_value in {
            "0",
            "false",
            "no",
            "off",
        }:
            return False

        return default

    def normalize_setting_value(
        self,
        key: str,
        value: Any,
    ) -> str:
        if key == SCAN_IMAGE_EXTENSIONS_KEY:
            extensions = self.normalize_scan_image_extensions(value)

            if not extensions:
                extensions = list(DEFAULT_SCAN_IMAGE_EXTENSIONS)

            return ",".join(extensions)

        if key in self.INT_SETTING_RULES:
            rule = self.INT_SETTING_RULES[key]
            parsed_value = self.parse_int(
                value,
                default=rule["default"],
            )
            parsed_value = self.clamp_int(
                value=parsed_value,
                minimum=rule["minimum"],
                maximum=rule["maximum"],
            )

            return str(parsed_value)

        if key in self.BOOL_SETTING_KEYS:
            return "true" if self.parse_bool(value) else "false"

        return str(value)

    def parse_int(
        self,
        value,
        default: int,
    ) -> int:
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    def clamp_int(
        self,
        value: int,
        minimum: int,
        maximum: int,
    ) -> int:
        return max(
            minimum,
            min(maximum, value),
        )

    def parse_bool(
        self,
        value,
    ) -> bool:
        return str(value).strip().lower() in {
            "1",
            "true",
            "yes",
            "on",
        }
