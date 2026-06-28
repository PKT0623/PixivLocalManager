from app.database import BookmarkArtworkRepository

from app.services.bookmark.importer import BookmarkArtworkImporter
from app.services.bookmark.matcher import BookmarkArtworkMatcher

from .preview_builder import BookmarkPreviewBuilderMixin
from .save_handler import BookmarkSaveHandlerMixin


class BookmarkService(
    BookmarkPreviewBuilderMixin,
    BookmarkSaveHandlerMixin,
):
    def __init__(self):
        self.repo = BookmarkArtworkRepository()
        self.matcher = BookmarkArtworkMatcher()
        self.importer = BookmarkArtworkImporter()

    def get_bookmark_artwork(
        self,
        bookmark_artwork_id: int,
    ):
        return self.repo.get_by_id(bookmark_artwork_id)

    def get_bookmark_artwork_by_artwork_id(
        self,
        artwork_id: str,
    ):
        return self.repo.get_by_artwork_id(artwork_id)

    def get_bookmark_artworks_by_artist_id(
        self,
        artist_id: str,
    ) -> list[dict]:
        return self.repo.get_by_artist_id(artist_id)

    def get_all_bookmark_artworks(self) -> list[dict]:
        return self.repo.get_all()

    def get_unmatched_bookmark_artworks(self) -> list[dict]:
        return self.repo.get_unmatched()

    def update_bookmark_artwork(
        self,
        bookmark_artwork_id: int,
        bookmark_artwork: dict,
        match_local_artist: bool = True,
    ) -> None:
        update_data = dict(bookmark_artwork)

        if match_local_artist:
            update_data = self.matcher.match_bookmark_artwork(update_data)

        return self.repo.update_bookmark_artwork(
            bookmark_artwork_id,
            update_data,
        )

    def match_all_bookmark_artworks(self) -> dict:
        return self.matcher.match_all()

    def toggle_favorite(
        self,
        bookmark_artwork_id: int,
    ) -> None:
        bookmark_artwork = self.repo.get_by_id(bookmark_artwork_id)

        if bookmark_artwork is None:
            raise ValueError("북마크 작품을 찾을 수 없습니다.")

        current_value = bool(bookmark_artwork.get("is_favorite", 0))

        return self.repo.update_favorite(
            bookmark_artwork_id,
            not current_value,
        )

    def toggle_hidden(
        self,
        bookmark_artwork_id: int,
    ) -> None:
        bookmark_artwork = self.repo.get_by_id(bookmark_artwork_id)

        if bookmark_artwork is None:
            raise ValueError("북마크 작품을 찾을 수 없습니다.")

        current_value = bool(bookmark_artwork.get("is_hidden", 0))

        return self.repo.update_hidden(
            bookmark_artwork_id,
            not current_value,
        )

    def delete_bookmark_artwork(
        self,
        bookmark_artwork_id: int,
    ) -> None:
        return self.repo.delete_bookmark_artwork(bookmark_artwork_id)

    def delete_all_bookmark_artworks(self) -> None:
        return self.repo.delete_all()
