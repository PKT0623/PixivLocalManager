import sys
from pathlib import Path

from PySide6.QtCore import QTimer
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from app.database import initialize_database
from ui.main_window import MainWindow
from ui.splash_screen import SplashScreen


SPLASH_MINIMUM_DISPLAY_MS = 500


def get_icon_path() -> str:
    if getattr(sys, "frozen", False):
        base_dir = Path(sys.executable).resolve().parent
    else:
        base_dir = Path(__file__).resolve().parent

    return str(base_dir / "assets" / "PLM.ico")


def main() -> None:
    app = QApplication(sys.argv)

    icon_path = get_icon_path()
    app.setWindowIcon(QIcon(icon_path))

    splash = SplashScreen()
    splash.show()
    app.processEvents()

    initialize_database()

    window = MainWindow()
    window.setWindowIcon(QIcon(icon_path))

    def show_main_window():
        window.show()
        splash.close()

    QTimer.singleShot(SPLASH_MINIMUM_DISPLAY_MS, show_main_window)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
