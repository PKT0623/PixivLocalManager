from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QPushButton,
    QTableWidgetItem,
    QWidget,
)


class ArtworkWidgetFactoryMixin:
    def create_readonly_item(
        self,
        text: str,
        alignment=Qt.AlignCenter,
    ) -> QTableWidgetItem:
        item = QTableWidgetItem(str(text))
        item.setTextAlignment(alignment)
        item.setFlags(item.flags() & ~Qt.ItemIsEditable)

        return item

    def create_small_button(self, text: str) -> QPushButton:
        button = QPushButton(text)
        button.setObjectName("smallActionButton")
        button.setCursor(Qt.PointingHandCursor)
        button.setFixedSize(60, 24)

        return button

    def create_centered_widget(self, widget) -> QWidget:
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addStretch()
        layout.addWidget(widget)
        layout.addStretch()

        return container

    def create_shortcut_widget(self, *buttons) -> QWidget:
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        layout.addStretch()

        for button in buttons:
            layout.addWidget(button)

        layout.addStretch()

        return container

    def get_existing_directory(
        self,
        parent,
        caption: str,
        directory: str,
    ) -> str:
        return QFileDialog.getExistingDirectory(
            parent,
            caption,
            directory,
        )
