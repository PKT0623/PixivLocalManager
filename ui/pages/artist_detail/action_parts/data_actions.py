from .data_actions_parts import (
    ArtistLoadActions,
    ArtistOperationsActions,
    ArtistSaveActions,
    ArtistUpdateHistoryActions,
)


class ArtistDataActions(
    ArtistLoadActions,
    ArtistOperationsActions,
    ArtistUpdateHistoryActions,
    ArtistSaveActions,
):
    pass
