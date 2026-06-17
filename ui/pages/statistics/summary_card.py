from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class StatisticsSummaryCard(QWidget):
    def __init__(self, title: str, value: str = "-"):
        super().__init__()

        self.title_label = QLabel(title)
        self.title_label.setObjectName("summaryCardTitle")

        self.value_label = QLabel(value)
        self.value_label.setObjectName("summaryCardValue")

        self._setup_ui()

    def _setup_ui(self):
        self.setObjectName("summaryCard")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setFixedHeight(68)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(3)

        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)

    def set_value(self, value):
        self.value_label.setText(str(value))
