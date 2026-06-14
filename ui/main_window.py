from PySide6.QtWidgets import QHBoxLayout, QMainWindow, QStackedWidget, QWidget

from ui.pages.artist_detail import ArtistDetailPage
from ui.pages.artists import ArtistsPage
from ui.pages.dashboard import DashboardPage
from ui.pages.scan_page import ScanPage
from ui.pages.settings import SettingsPage
from ui.widgets.sidebar import Sidebar


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Pixiv Local Manager")
        self.resize(1200, 800)

        self.sidebar = Sidebar()
        self.page_stack = QStackedWidget()

        self.pages = {
            "dashboard": DashboardPage(),
            "scan": ScanPage(),
            "artists": ArtistsPage(),
            "artist_detail": ArtistDetailPage(),
            "settings": SettingsPage(),
        }

        self._setup_ui()
        self._connect_signals()

        self.show_page("dashboard")

    def _setup_ui(self):
        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)

        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.page_stack, 1)

        for page in self.pages.values():
            self.page_stack.addWidget(page)

        self.setCentralWidget(central_widget)

    def _connect_signals(self):
        self.sidebar.page_changed.connect(self.show_page)

        artists_page = self.pages.get("artists")
        if hasattr(artists_page, "artist_selected"):
            artists_page.artist_selected.connect(self.show_artist_detail)

        detail_page = self.pages.get("artist_detail")
        if hasattr(detail_page, "back_requested"):
            detail_page.back_requested.connect(lambda: self.show_page("artists"))

        if hasattr(detail_page, "artist_updated"):
            detail_page.artist_updated.connect(self._handle_artist_updated)

    def show_page(self, page_name: str):
        page = self.pages.get(page_name)

        if page is None:
            return

        if page_name == "artists" and hasattr(page, "load_artists"):
            page.load_artists()

        self.page_stack.setCurrentWidget(page)
        self.sidebar.set_active_page(page_name)

    def show_artist_detail(self, artist_id: int):
        detail_page = self.pages.get("artist_detail")

        if detail_page is None:
            return

        if hasattr(detail_page, "set_artist"):
            detail_page.set_artist(artist_id)

        self.show_page("artist_detail")

    def _handle_artist_updated(self, artist_id: int):
        artists_page = self.pages.get("artists")

        if artists_page is None:
            return

        if hasattr(artists_page, "load_artists"):
            artists_page.load_artists()
