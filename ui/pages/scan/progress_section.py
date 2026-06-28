from PySide6.QtWidgets import QWidget

from .progress_section_parts import (
    ScanProgressResetActionsMixin,
    ScanProgressUiFactoryMixin,
    ScanProgressUpdateActionsMixin,
)


class ScanProgressSection(
    QWidget,
    ScanProgressUiFactoryMixin,
    ScanProgressResetActionsMixin,
    ScanProgressUpdateActionsMixin,
):
    def __init__(self):
        super().__init__()

        self.summary_labels = {}

        self._setup_ui()
