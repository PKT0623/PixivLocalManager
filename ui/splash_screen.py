import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


SPLASH_SIZE = 460


def get_asset_path(file_name: str) -> Path:
    if getattr(sys, "frozen", False):
        base_dir = Path(sys.executable).resolve().parent
    else:
        base_dir = Path(__file__).resolve().parent.parent

    return base_dir / "assets" / file_name


class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Pixiv Local Manager")
        self.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.SplashScreen
        )
        self.setAttribute(Qt.WA_TranslucentBackground)

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)

        splash_path = get_asset_path("splash.png")
        pixmap = QPixmap(str(splash_path))

        if not pixmap.isNull():
            pixmap = pixmap.scaled(
                SPLASH_SIZE,
                SPLASH_SIZE,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
            self.image_label.setPixmap(pixmap)
        else:
            self.image_label.setText("Pixiv Local Manager")
            self.image_label.setFixedSize(SPLASH_SIZE, SPLASH_SIZE)
            self.image_label.setStyleSheet(
                """
                QLabel {
                    background-color: #0d6efd;
                    color: white;
                    font-size: 28px;
                    font-weight: bold;
                    padding: 80px;
                    border-radius: 24px;
                }
                """
            )

        layout.addWidget(self.image_label)
