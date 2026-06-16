from .action_parts import (
    ArtistArtworkActions,
    ArtistDataActions,
    ArtistDialogActions,
    ArtistTagActions,
)


class ArtistDetailActions(
    ArtistDataActions,
    ArtistArtworkActions,
    ArtistTagActions,
    ArtistDialogActions,
):
    def __init__(self, page):
        self.page = page
