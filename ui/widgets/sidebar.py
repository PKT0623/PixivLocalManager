from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QLabel, QPushButton, QVBoxLayout


class Sidebar(QFrame):
    page_changed = Signal(str)

    def __init__(self):
        super().__init__()

        self.buttons = {}

        self._setup_ui()

    def _setup_ui(self):
        self.setFixedWidth(220)
        self.setObjectName("sidebar")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 20, 16, 20)
        layout.setSpacing(10)

        title_label = QLabel("Pixiv Manager")
        title_label.setObjectName("sidebarTitle")

        layout.addWidget(title_label)
        layout.addSpacing(20)

        self._add_button(layout, "dashboard", "대시보드")
        self._add_button(layout, "scan", "폴더 스캔")
        self._add_button(layout, "update_check", "업데이트 확인")
        self._add_button(layout, "artists", "작가 목록")

        layout.addStretch()

        self._add_button(layout, "settings", "설정")

        self.setStyleSheet(
            """
            QFrame#sidebar {
                background-color: #202124;
            }

            QLabel#sidebarTitle {
                color: #ffffff;
                font-size: 20px;
                font-weight: 700;
            }

            QPushButton {
                background-color: transparent;
                color: #d0d0d0;
                border: none;
                border-radius: 8px;
                padding: 12px 14px;
                text-align: left;
                font-size: 15px;
            }

            QPushButton:hover {
                background-color: #303134;
                color: #ffffff;
            }

            QPushButton[active="true"] {
                background-color: #3c4043;
                color: #ffffff;
                font-weight: 700;
            }
            """
        )

    def _add_button(self, layout: QVBoxLayout, page_name: str, text: str):
        button = QPushButton(text)
        button.setCursor(Qt.PointingHandCursor)
        button.clicked.connect(
            lambda checked=False, name=page_name: self.page_changed.emit(name)
        )

        self.buttons[page_name] = button
        layout.addWidget(button)

    def set_active_page(self, page_name: str):
        for name, button in self.buttons.items():
            is_active = name == page_name
            button.setProperty("active", is_active)
            button.style().unpolish(button)
            button.style().polish(button)
