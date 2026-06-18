import csv
import re
from pathlib import Path


class BookmarkArtworkImporter:
    ARTWORK_URL_PATTERN = re.compile(
        r"pixiv\.net/(?:artworks|member_illust\.php\?.*illust_id=)/?(\d+)"
    )
    NUMBER_LINE_PATTERN = re.compile(r"^\d{5,}$")

    def parse_txt_file(
        self,
        file_path: str,
    ) -> list[dict]:
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError("파일을 찾을 수 없습니다.")

        bookmark_artworks = []

        with path.open("r", encoding="utf-8-sig") as file:
            for line in file:
                bookmark_artworks.extend(
                    self.parse_text_line(line)
                )

        return bookmark_artworks

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

        artwork_id = self.extract_id(text)

        if not artwork_id:
            return []

        return [
            {
                "artwork_id": artwork_id,
                "title": "",
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

        url_match = self.ARTWORK_URL_PATTERN.search(text)

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
        bookmark_artworks = []

        for row in reader:
            artwork_id = self._get_row_value(
                row,
                [
                    "artwork_id",
                    "illust_id",
                    "work_id",
                    "id",
                    "pixiv_id",
                ],
            )

            artwork_id = self.extract_id(artwork_id)

            if not artwork_id:
                continue

            bookmark_artworks.append(
                {
                    "artwork_id": artwork_id,
                    "title": self._get_row_value(
                        row,
                        [
                            "title",
                            "artwork_title",
                            "illust_title",
                        ],
                    ),
                    "artist_id": self.extract_id(
                        self._get_row_value(
                            row,
                            [
                                "artist_id",
                                "user_id",
                                "author_id",
                            ],
                        )
                    ),
                    "artist_name": self._get_row_value(
                        row,
                        [
                            "artist_name",
                            "user_name",
                            "author_name",
                        ],
                    ),
                    "bookmark_count": self._to_int(
                        self._get_row_value(
                            row,
                            [
                                "bookmark_count",
                                "bookmarks",
                                "bookmark",
                            ],
                        )
                    ),
                    "page_count": self._to_int(
                        self._get_row_value(
                            row,
                            [
                                "page_count",
                                "pages",
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

        return bookmark_artworks

    def _parse_csv_without_header(
        self,
        file,
    ) -> list[dict]:
        reader = csv.reader(file)
        bookmark_artworks = []

        for row in reader:
            if not row:
                continue

            artwork_id = self.extract_id(row[0])

            if not artwork_id:
                continue

            title = ""

            if len(row) >= 2:
                title = str(row[1]).strip()

            bookmark_artworks.append(
                {
                    "artwork_id": artwork_id,
                    "title": title,
                    "source_type": "csv",
                }
            )

        return bookmark_artworks

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
