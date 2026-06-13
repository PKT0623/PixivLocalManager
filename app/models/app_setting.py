from dataclasses import dataclass


@dataclass
class AppSetting:
    key: str
    value: str
