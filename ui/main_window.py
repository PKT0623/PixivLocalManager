from PySide6.QtWidgets import QHBoxLayout, QMainWindow, QStackedWidget, QWidget

from app.services.backup import DatabaseBackupService
from app.services.settings_service import SettingsService
from ui.pages import (
    ArtistDetailPage,
    ArtistsPage,
    DashboardPage,
    ScanPage,
    SettingsPage,
    UpdateCheckPage,
)
from ui.widgets import Sidebar


class MainWindow(QMainWindow):
    DEFAULT_WIDTH = 1500
    DEFAULT_HEIGHT = 900
    MIN_WIDTH = 1200
    MIN_HEIGHT = 760

    def __init__(self):
        super().__init__()

        self.settings_service = SettingsService()
        self.should_restore_maximized = False
        self.did_restore_window_state = False

        self.setWindowTitle("Pixiv Local Manager")
        self.resize(self.DEFAULT_WIDTH, self.DEFAULT_HEIGHT)
        self.setMinimumSize(self.MIN_WIDTH, self.MIN_HEIGHT)
        self._restore_window_geometry()

        self.previous_page = "artists"

        self.sidebar = Sidebar()
        self.page_stack = QStackedWidget()
        self.pages = self._create_pages()

        self._setup_ui()
        self._connect_signals()
        self._run_startup_auto_backup()

        self.show_page("dashboard")

    def _create_pages(self) -> dict[str, QWidget]:
        return {
            "dashboard": DashboardPage(),
            "scan": ScanPage(),
            "update_check": UpdateCheckPage(),
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

        dashboard_page = self.pages["dashboard"]
        artists_page = self.pages["artists"]
        scan_page = self.pages["scan"]
        detail_page = self.pages["artist_detail"]

        dashboard_page.artist_detail_requested.connect(
            self.show_artist_detail
        )
        artists_page.artist_selected.connect(self.show_artist_detail)
        scan_page.artist_detail_requested.connect(self.show_artist_detail)

        detail_page.back_requested.connect(self.go_back_from_artist_detail)
        detail_page.artist_updated.connect(self._handle_artist_updated)

    def _run_startup_auto_backup(self):
        try:
            DatabaseBackupService().run_startup_auto_backup()
        except Exception:
            return

        settings_page = self.pages.get("settings")

        if settings_page is not None:
            settings_page.actions.refresh_backup_list()

    def _restore_window_geometry(self):
        self.should_restore_maximized = self.settings_service.get_bool_setting(
            "window_maximized",
            False,
        )

        if self.should_restore_maximized:
            return

        width = self.settings_service.get_int_setting(
            "window_width",
            self.DEFAULT_WIDTH,
        )
        height = self.settings_service.get_int_setting(
            "window_height",
            self.DEFAULT_HEIGHT,
        )
        x = self.settings_service.get_setting("window_x")
        y = self.settings_service.get_setting("window_y")

        width = max(self.MIN_WIDTH, width)
        height = max(self.MIN_HEIGHT, height)

        self.resize(
            width,
            height,
        )

        if x is None or y is None:
            return

        try:
            self.move(
                int(x),
                int(y),
            )
        except (TypeError, ValueError):
            return

    def _save_window_geometry(self):
        self.settings_service.set_setting(
            "window_maximized",
            self.isMaximized(),
        )

        if self.isMaximized():
            return

        size = self.size()
        position = self.pos()

        self.settings_service.set_setting(
            "window_width",
            size.width(),
        )
        self.settings_service.set_setting(
            "window_height",
            size.height(),
        )
        self.settings_service.set_setting(
            "window_x",
            position.x(),
        )
        self.settings_service.set_setting(
            "window_y",
            position.y(),
        )

    def show_page(self, page_name: str):
        page = self.pages.get(page_name)

        if page is None:
            return

        if page_name == "artists":
            page.load_artists()

        if page_name == "update_check":
            page.load_artists()

        if page_name == "settings":
            page.actions.refresh_backup_list()
            page.actions.refresh_database_info()
            page.actions.refresh_environment_info()

        self.page_stack.setCurrentWidget(page)
        self.sidebar.set_active_page(page_name)

    def show_artist_detail(self, artist_id: int):
        current_page_name = self._get_current_page_name()

        if (
            current_page_name is not None
            and current_page_name != "artist_detail"
        ):
            self.previous_page = current_page_name

        detail_page = self.pages["artist_detail"]
        detail_page.set_artist(artist_id)

        self.show_page("artist_detail")

    def go_back_from_artist_detail(self):
        target_page = self.previous_page

        if target_page == "artist_detail":
            target_page = "artists"

        self.show_page(target_page)

    def _get_current_page_name(self):
        current_widget = self.page_stack.currentWidget()

        for page_name, page in self.pages.items():
            if page is current_widget:
                return page_name

        return None

    def _handle_artist_updated(self, artist_id: int):
        artists_page = self.pages["artists"]
        artists_page.load_artists()

    def showEvent(self, event):
        super().showEvent(event)

        if self.did_restore_window_state:
            return

        self.did_restore_window_state = True

        if self.should_restore_maximized:
            self.showMaximized()

    def closeEvent(self, event):
        self._save_window_geometry()

        update_page = self.pages.get("update_check")

        if update_page is not None:
            update_page.shutdown_worker()

        super().closeEvent(event)
