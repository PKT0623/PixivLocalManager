import re


class FolderNameMixin:
    BRACKETED_PIXIV_ID_PATTERN = re.compile(r"[\[\(](\d{5,})[\]\)]")
    TRAILING_PIXIV_ID_PATTERN = re.compile(r"[-_ ]+(\d{5,})$")
    ANY_PIXIV_ID_PATTERN = re.compile(r"(\d{5,})")

    def parse_artist_folder_name(
        self,
        folder_name: str,
    ) -> tuple[str, str]:
        folder_name = folder_name.strip()

        match = self._find_pixiv_id_match(folder_name)

        if match is None:
            return folder_name, ""

        pixiv_id = match.group(1)

        artist_name = (
            folder_name[: match.start()]
            + folder_name[match.end():]
        )
        artist_name = artist_name.strip(" _-")

        return artist_name.strip(), pixiv_id

    def get_folder_name_rule_status(
        self,
        folder_name: str,
    ) -> dict:
        folder_name = folder_name.strip()

        if not folder_name:
            return {
                "level": "error",
                "message": "폴더명이 비어 있습니다.",
            }

        trailing_match = self.TRAILING_PIXIV_ID_PATTERN.search(folder_name)

        if trailing_match is not None:
            return {
                "level": "ok",
                "message": "권장 폴더명 형식입니다.",
            }

        bracket_matches = list(
            self.BRACKETED_PIXIV_ID_PATTERN.finditer(folder_name)
        )

        if bracket_matches:
            return {
                "level": "ok",
                "message": "권장 폴더명 형식입니다.",
            }

        any_matches = list(
            self.ANY_PIXIV_ID_PATTERN.finditer(folder_name)
        )

        if any_matches:
            return {
                "level": "warning",
                "message": (
                    "Pixiv ID는 찾았지만 폴더명 형식이 애매합니다. "
                    "권장 형식은 '작가명-12345678' 또는 "
                    "'작가명 [12345678]'입니다."
                ),
            }

        return {
            "level": "error",
            "message": "폴더명에서 Pixiv ID를 찾을 수 없습니다.",
        }

    def _find_pixiv_id_match(
        self,
        folder_name: str,
    ):
        trailing_match = self.TRAILING_PIXIV_ID_PATTERN.search(folder_name)

        if trailing_match is not None:
            return trailing_match

        bracket_matches = list(
            self.BRACKETED_PIXIV_ID_PATTERN.finditer(folder_name)
        )

        if bracket_matches:
            return bracket_matches[-1]

        any_matches = list(
            self.ANY_PIXIV_ID_PATTERN.finditer(folder_name)
        )

        if any_matches:
            return any_matches[-1]

        return None
