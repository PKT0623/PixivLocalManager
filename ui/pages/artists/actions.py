from .action_parts import (
    ArtistsBulkActions,
    ArtistsDataActions,
    ArtistsDialogActions,
)


class ArtistsActions(
    ArtistsDataActions,
    ArtistsBulkActions,
    ArtistsDialogActions,
):
    def __init__(self, page):
        self.page = page
