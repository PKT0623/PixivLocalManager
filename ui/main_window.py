from PySide6.QtWidgets import QHBoxLayout, QMainWindow, QStackedWidget, QWidget

from ui.pages import (
    ArtistDetailPage,
    ArtistsPage,
    DashboardPage,
    ScanPage,
    SettingsPage,
)
from ui.widgets import Sidebar


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Pixiv Local Manager")
        self.resize(1500, 900)
        self.setMinimumSize(1200, 760)

        self.sidebar = Sidebar()
        self.page_stack = QStackedWidget()
        self.pages = self._create_pages()

        self._setup_ui()
        self._connect_signals()

        self.show_page("dashboard")

    def _create_pages(self) -> dict[str, QWidget]:
        return {
            "dashboard": DashboardPage(),
            "scan": ScanPage(),
            "artists": ArtistsPage(),
            "artist_detail": ArtistDetailPage(),
            "settings": SettingsPage(),
        }

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

        artists_page = self.pages["artists"]
        scan_page = self.pages["scan"]
        detail_page = self.pages["artist_detail"]

        artists_page.artist_selected.connect(self.show_artist_detail)
        scan_page.artist_detail_requested.connect(self.show_artist_detail)

        detail_page.back_requested.connect(lambda: self.show_page("artists"))
        detail_page.artist_updated.connect(self._handle_artist_updated)

    def show_page(self, page_name: str):
        page = self.pages.get(page_name)

        if page is None:
            return

        if page_name == "artists":
            page.load_artists()

        self.page_stack.setCurrentWidget(page)
        self.sidebar.set_active_page(page_name)

    def show_artist_detail(self, artist_id: int):
        detail_page = self.pages["artist_detail"]
        detail_page.set_artist(artist_id)

        self.show_page("artist_detail")

    def _handle_artist_updated(self, artist_id: int):
        artists_page = self.pages["artists"]
        artists_page.load_artists()
