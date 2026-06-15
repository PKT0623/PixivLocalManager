from dataclasses import dataclass


@dataclass(frozen=True)
class ArtistTableColumn:
    index: int
    header: str
    sort_field: str | None = None
    width: int | None = None


COLUMNS = [
    ArtistTableColumn(0, "No", None, 50),
    ArtistTableColumn(1, "즐겨찾기", None, 70),
    ArtistTableColumn(2, "작가명", "artist_name"),
    ArtistTableColumn(3, "Pixiv ID", "pixiv_id", 85),
    ArtistTableColumn(4, "작품 수", "folder_artwork_count", 65),
    ArtistTableColumn(5, "파일 수", "folder_file_count", 65),
    ArtistTableColumn(6, "상태", None, 120),
    ArtistTableColumn(7, "평점", "rating", 100),
    ArtistTableColumn(8, "태그"),
    ArtistTableColumn(9, "최근 열람", "last_viewed_at", 120),
    ArtistTableColumn(10, "등록일", "created_at", 120),
    ArtistTableColumn(11, "메모"),
    ArtistTableColumn(12, "바로가기", None, 200),
]

COLUMN_HEADERS = [
    column.header
    for column in COLUMNS
]

COLUMN_SORT_FIELDS = {
    column.index: column.sort_field
    for column in COLUMNS
    if column.sort_field is not None
}

COLUMN_NO = 0
COLUMN_FAVORITE = 1
COLUMN_ARTIST_NAME = 2
COLUMN_PIXIV_ID = 3
COLUMN_ARTWORK_COUNT = 4
COLUMN_FILE_COUNT = 5
COLUMN_STATUS = 6
COLUMN_RATING = 7
COLUMN_TAGS = 8
COLUMN_LAST_VIEWED_AT = 9
COLUMN_CREATED_AT = 10
COLUMN_MEMO = 11
COLUMN_SHORTCUTS = 12
