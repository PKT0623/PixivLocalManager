from .constants import (
    DEFAULT_SCAN_IMAGE_EXTENSIONS,
    SCAN_IMAGE_EXTENSIONS_KEY,
)


class ScanSettingsMixin:
    SCAN_IMAGE_EXTENSIONS_KEY = SCAN_IMAGE_EXTENSIONS_KEY
    DEFAULT_SCAN_IMAGE_EXTENSIONS = DEFAULT_SCAN_IMAGE_EXTENSIONS

    def get_scan_image_extensions(self) -> list[str]:
        value = self.get_setting(self.SCAN_IMAGE_EXTENSIONS_KEY)

        if value is None or str(value).strip() == "":
            return list(self.DEFAULT_SCAN_IMAGE_EXTENSIONS)

        extensions = self.normalize_scan_image_extensions(value)

        if not extensions:
            return list(self.DEFAULT_SCAN_IMAGE_EXTENSIONS)

        return extensions

    def set_scan_image_extensions(
        self,
        extensions,
    ):
        normalized_extensions = self.normalize_scan_image_extensions(
            extensions
        )

        if not normalized_extensions:
            normalized_extensions = list(
                self.DEFAULT_SCAN_IMAGE_EXTENSIONS
            )

        return self.set_setting(
            self.SCAN_IMAGE_EXTENSIONS_KEY,
            ",".join(normalized_extensions),
        )

    def reset_scan_image_extensions(self):
        return self.set_scan_image_extensions(
            self.DEFAULT_SCAN_IMAGE_EXTENSIONS
        )

    def normalize_scan_image_extensions(
        self,
        extensions,
    ) -> list[str]:
        if extensions is None:
            return []

        if isinstance(extensions, str):
            raw_extensions = extensions.replace(";", ",").split(",")
        else:
            raw_extensions = list(extensions)

        normalized_extensions = []

        for extension in raw_extensions:
            extension = str(extension or "").strip().lower()

            if not extension:
                continue

            if extension.startswith("."):
                extension = extension[1:]

            extension = "".join(
                character
                for character in extension
                if character.isalnum()
            )

            if not extension:
                continue

            if extension in normalized_extensions:
                continue

            normalized_extensions.append(extension)

        return normalized_extensions

    def get_scan_image_extension_set(self) -> set[str]:
        return {
            f".{extension}"
            for extension in self.get_scan_image_extensions()
        }
