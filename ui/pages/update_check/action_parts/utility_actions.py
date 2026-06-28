from .utility_actions_parts import (
    UpdateCheckDownloadPlanActionsMixin,
    UpdateCheckLogActionsMixin,
    UpdateCheckPhpsessidActionsMixin,
    UpdateCheckRescanActionsMixin,
)


class UpdateCheckUtilityActions(
    UpdateCheckPhpsessidActionsMixin,
    UpdateCheckLogActionsMixin,
    UpdateCheckDownloadPlanActionsMixin,
    UpdateCheckRescanActionsMixin,
):
    pass
