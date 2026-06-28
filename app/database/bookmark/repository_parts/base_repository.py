from app.database.bookmark.update_repository import (
    BookmarkArtworkUpdateRepository,
)

from .mutation_repository import BookmarkArtworkMutationRepository
from .query_repository import BookmarkArtworkQueryRepository


class BookmarkArtworkRepository(
    BookmarkArtworkMutationRepository,
    BookmarkArtworkQueryRepository,
    BookmarkArtworkUpdateRepository,
):
    pass
