from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QSizePolicy


class StatusBadge(QLabel):
    STATUS_CONFIG = {
        "unknown": {
            "label": "미확인",
            "background": "#6c757d",
            "color": "#ffffff",
        },
        "latest": {
            "label": "최신",
            "background": "#198754",
            "color": "#ffffff",
        },
        "up_to_date": {
            "label": "최신",
            "background": "#198754",
            "color": "#ffffff",
        },
        "need_update": {
            "label": "업데이트 필요",
            "background": "#fd7e14",
            "color": "#ffffff",
        },
        "updated": {
            "label": "업데이트 완료",
            "background": "#0d6efd",
            "color": "#ffffff",
        },
        "error": {
            "label": "오류",
            "background": "#dc3545",
            "color": "#ffffff",
        },
        "active": {
            "label": "활성",
            "background": "#0d6efd",
            "color": "#ffffff",
        },
        "inactive": {
            "label": "비활성",
            "background": "#6c757d",
            "color": "#ffffff",
        },
    }

    DEFAULT_CONFIG = {
        "label": "-",
        "background": "#adb5bd",
        "color": "#ffffff",
    }

    def __init__(self, status=None, parent=None):
        super().__init__(parent)

        self.setAlignment(Qt.AlignCenter)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.set_status(status)

    def set_status(self, status):
        status_key = str(status or "").strip()
        config = self.STATUS_CONFIG.get(status_key, self.DEFAULT_CONFIG)

        self.setText(config["label"])
        self.setStyleSheet(
            f"""
            QLabel {{
                background-color: {config["background"]};
                color: {config["color"]};
                border-radius: 0px;
                padding: 0px;
                font-size: 13px;
                font-weight: 600;
            }}
            """
        )
