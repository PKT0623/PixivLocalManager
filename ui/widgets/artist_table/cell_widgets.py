from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QPushButton, QSizePolicy, QWidget

from ui.widgets.status_badge import StatusBadge


def create_status_badge(status):
    return StatusBadge(status)


def create_favorite_button(
    artist_id,
    is_favorite,
    toggle_callback,
):
    button = QPushButton("★" if is_favorite else "☆")
    button.setCursor(Qt.PointingHandCursor)
    button.setMinimumHeight(42)
    button.setSizePolicy(
        QSizePolicy.Expanding,
        QSizePolicy.Expanding,
    )

    if is_favorite:
        button.setStyleSheet(
            """
            QPushButton {
                border: 1px solid #c69500;
                border-radius: 0px;
                background-color: #ffc107;
                color: #5f4300;
                font-size: 22px;
                font-weight: 800;
                padding: 0px;
                margin: 0px;
            }

            QPushButton:hover {
                background-color: #ffb300;
            }
            """
        )
    else:
        button.setStyleSheet(
            """
            QPushButton {
                border: 1px solid #d0d0d0;
                border-radius: 0px;
                background-color: #ececec;
                color: #777777;
                font-size: 22px;
                font-weight: 800;
                padding: 0px;
                margin: 0px;
            }

            QPushButton:hover {
                background-color: #e0e0e0;
            }
            """
        )

    if artist_id is not None:
        button.clicked.connect(
            lambda checked=False: toggle_callback(int(artist_id))
        )

    return button


def create_shortcut_buttons(
    folder_path,
    pixiv_id,
    open_folder_callback,
    open_pixiv_callback,
):
    widget = QWidget()
    layout = QHBoxLayout(widget)

    layout.setContentsMargins(6, 2, 6, 2)
    layout.setSpacing(6)

    folder_path = str(folder_path or "").strip()
    pixiv_id = str(pixiv_id or "").strip()

    folder_button = QPushButton("폴더")
    folder_button.setEnabled(bool(folder_path))
    folder_button.setMinimumWidth(75)
    folder_button.setMinimumHeight(30)

    pixiv_button = QPushButton("Pixiv")
    pixiv_button.setEnabled(bool(pixiv_id))
    pixiv_button.setMinimumWidth(75)
    pixiv_button.setMinimumHeight(30)

    if folder_path:
        folder_button.clicked.connect(
            lambda checked=False: open_folder_callback(folder_path)
        )

    if pixiv_id:
        pixiv_button.clicked.connect(
            lambda checked=False: open_pixiv_callback(pixiv_id)
        )

    layout.addWidget(folder_button)
    layout.addWidget(pixiv_button)

    return widget
