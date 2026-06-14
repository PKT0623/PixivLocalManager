from PySide6.QtWidgets import QPushButton

from ui.widgets.status_badge import StatusBadge


def create_status_badge(status):
    return StatusBadge(status)


def create_pixiv_button(pixiv_id, open_callback):
    pixiv_id = str(pixiv_id or "").strip()

    button = QPushButton("열기")
    button.setEnabled(bool(pixiv_id))

    if pixiv_id:
        button.clicked.connect(
            lambda checked=False: open_callback(pixiv_id)
        )

    return button
