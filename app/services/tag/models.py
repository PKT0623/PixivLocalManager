from dataclasses import dataclass


@dataclass
class TagData:
    original: str = ""
    translated: str = ""
    artwork_count: int = 0
    file_count: int = 0
    custom_translation: bool = False

    def to_dict(self) -> dict:
        return {
            "original": self.original,
            "translated": self.translated,
            "artwork_count": self.artwork_count,
            "file_count": self.file_count,
            "custom_translation": self.custom_translation,
        }

