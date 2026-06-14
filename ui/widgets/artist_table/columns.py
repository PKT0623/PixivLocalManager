from dataclasses import dataclass


@dataclass(frozen=True)
class ArtistTableColumn:
    index: int
    header: str
    sort_field: str | None = None
    width: int | None = None


COLUMNS = [
    ArtistTableColumn(0, "No"),
    ArtistTableColumn(1, "작가명", "artist_name"),
    ArtistTableColumn(2, "Pixiv ID"),
    ArtistTableColumn(3, "작품 수", "folder_artwork_count"),
    ArtistTableColumn(4, "상태", "update_status", 120),
    ArtistTableColumn(5, "평점", "rating", 100),
    ArtistTableColumn(6, "메모"),
    ArtistTableColumn(7, "Pixiv", None, 80),
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
COLUMN_ARTIST_NAME = 1
COLUMN_PIXIV_ID = 2
COLUMN_ARTWORK_COUNT = 3
COLUMN_STATUS = 4
COLUMN_RATING = 5
COLUMN_MEMO = 6
COLUMN_PIXIV_BUTTON = 7
