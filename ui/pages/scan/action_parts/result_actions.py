from .result_actions_parts import (
    ScanResultCompareActionsMixin,
    ScanResultExportActionsMixin,
    ScanResultFailedActionsMixin,
    ScanResultHistoryActionsMixin,
    ScanResultSettingsActionsMixin,
)


class ScanResultActions(
    ScanResultFailedActionsMixin,
    ScanResultExportActionsMixin,
    ScanResultHistoryActionsMixin,
    ScanResultSettingsActionsMixin,
    ScanResultCompareActionsMixin,
):
    pass
