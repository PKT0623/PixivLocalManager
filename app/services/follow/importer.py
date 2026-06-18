import csv
import re
from pathlib import Path


class FollowUserImporter:
    USER_URL_PATTERN = re.compile(
        r"pixiv\.net/(?:users|member\.php\?id=)/?(\d+)"
    )
    NUMBER_LINE_PATTERN = re.compile(r"^\d{5,}$")

    def parse_txt_file(
        self,
        file_path: str,
    ) -> list[dict]:
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError("파일을 찾을 수 없습니다.")

        follow_users = []

        with path.open("r", encoding="utf-8-sig") as file:
            for line in file:
                follow_users.extend(
                    self.parse_text_line(line)
                )

        return follow_users

    def parse_csv_file(
        self,
        file_path: str,
    ) -> list[dict]:
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError("파일을 찾을 수 없습니다.")

        with path.open("r", encoding="utf-8-sig", newline="") as file:
            sample = file.read(2048)
            file.seek(0)

            has_header = csv.Sniffer().has_header(sample)

            if has_header:
                return self._parse_csv_with_header(file)

            return self._parse_csv_without_header(file)

    def parse_text_line(
        self,
        line: str,
    ) -> list[dict]:
        text = line.strip()

        if self._should_skip_line(text):
            return []

        pixiv_user_id = self.extract_id(text)

        if not pixiv_user_id:
            return []

        return [
            {
                "pixiv_user_id": pixiv_user_id,
                "user_name": "",
                "source_type": "txt",
            }
        ]

    def extract_id(
        self,
        value,
    ) -> str:
        if value is None:
            return ""

        text = str(value).strip()

        if not text:
            return ""

        url_match = self.USER_URL_PATTERN.search(text)

        if url_match:
            return url_match.group(1)

        if self.NUMBER_LINE_PATTERN.match(text):
            return text

        return ""

    def _should_skip_line(
        self,
        text: str,
    ) -> bool:
        if not text:
            return True

        lowered_text = text.lower()

        if text.startswith("###"):
            return True

        skip_keywords = [
            "export members date",
            "export images date",
            "end-of-file",
        ]

        return any(keyword in lowered_text for keyword in skip_keywords)

    def _parse_csv_with_header(
        self,
        file,
    ) -> list[dict]:
        reader = csv.DictReader(file)
        follow_users = []

        for row in reader:
            pixiv_user_id = self._get_row_value(
                row,
                [
                    "pixiv_user_id",
                    "user_id",
                    "uid",
                    "id",
                    "pixiv_id",
                ],
            )

            pixiv_user_id = self.extract_id(pixiv_user_id)

            if not pixiv_user_id:
                continue

            follow_users.append(
                {
                    "pixiv_user_id": pixiv_user_id,
                    "user_name": self._get_row_value(
                        row,
                        [
                            "user_name",
                            "name",
                            "artist_name",
                            "username",
                        ],
                    ),
                    "profile_image_url": self._get_row_value(
                        row,
                        [
                            "profile_image_url",
                            "profile_image",
                            "image_url",
                            "avatar",
                        ],
                    ),
                    "comment": self._get_row_value(
                        row,
                        [
                            "comment",
                            "description",
                            "bio",
                        ],
                    ),
                    "artwork_count": self._to_int(
                        self._get_row_value(
                            row,
                            [
                                "artwork_count",
                                "illust_count",
                                "works",
                            ],
                        )
                    ),
                    "file_count": self._to_int(
                        self._get_row_value(
                            row,
                            [
                                "file_count",
                                "files",
                            ],
                        )
                    ),
                    "pixiv_tags": self._get_row_value(
                        row,
                        [
                            "pixiv_tags",
                            "tags",
                        ],
                    ),
                    "source_type": "csv",
                }
            )

        return follow_users

    def _parse_csv_without_header(
        self,
        file,
    ) -> list[dict]:
        reader = csv.reader(file)
        follow_users = []

        for row in reader:
            if not row:
                continue

            pixiv_user_id = self.extract_id(row[0])

            if not pixiv_user_id:
                continue

            user_name = ""

            if len(row) >= 2:
                user_name = str(row[1]).strip()

            follow_users.append(
                {
                    "pixiv_user_id": pixiv_user_id,
                    "user_name": user_name,
                    "source_type": "csv",
                }
            )

        return follow_users

    def _get_row_value(
        self,
        row: dict,
        keys: list[str],
    ) -> str:
        normalized_row = {
            str(key).strip().lower(): value
            for key, value in row.items()
        }

        for key in keys:
            value = normalized_row.get(key.lower())

            if value is not None:
                return str(value).strip()

        return ""

    def _to_int(
        self,
        value,
    ) -> int:
        try:
            return int(value or 0)
        except (TypeError, ValueError):
            return 0
