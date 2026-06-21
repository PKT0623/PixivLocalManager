from PySide6.QtCore import Signal
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from app.services.artist import ArtistService
from ui.widgets.artist_table import ArtistTable

from .actions import ArtistsActions
from .toolbar import ArtistsToolbar


class ArtistsPage(QWidget):
    artist_selected = Signal(int)

    def __init__(self):
        super().__init__()

        self.artist_service = ArtistService()
        self.all_artists = []
        self.rating_display_mode = "stars"

        self.default_sort_rules = [
            ("artist_name", False),
        ]
        self.sort_rules = self.default_sort_rules.copy()

        self.actions = ArtistsActions(self)

        self._setup_ui()
        self._connect_signals()

        self.actions.load_artists()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(16)

        title_label = QLabel("작가 목록")
        title_label.setObjectName("pageTitle")

        self.toolbar = ArtistsToolbar()
        self.artist_table = ArtistTable()

        layout.addWidget(title_label)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.artist_table, 1)

        self.setStyleSheet(
            """
            QLabel#pageTitle {
                font-size: 28px;
                font-weight: 700;
            }

            QLineEdit {
                padding: 8px 10px;
                border: 1px solid #cccccc;
                border-radius: 6px;
                font-size: 14px;
            }

            QComboBox {
                padding: 6px 10px;
                border: 1px solid #cccccc;
                border-radius: 6px;
                background-color: #ffffff;
                font-size: 14px;
            }

            QComboBox::drop-down {
                width: 24px;
                border: none;
            }

            QCheckBox {
                font-size: 14px;
                spacing: 6px;
            }

            QPushButton {
                padding: 7px 12px;
                border: 1px solid #cccccc;
                border-radius: 6px;
                background-color: #f5f5f5;
                font-size: 14px;
            }

            QPushButton:hover {
                background-color: #eeeeee;
            }
            """
        )

    def _connect_signals(self):
        self.toolbar.search_mode_combo.currentIndexChanged.connect(
            self.actions.apply_filter_and_sort
        )
        self.toolbar.search_input.textChanged.connect(
            self.actions.apply_filter_and_sort
        )
        self.toolbar.rating_filter_input.textChanged.connect(
            self.actions.apply_filter_and_sort
        )
        self.toolbar.rating_filter_mode_button.clicked.connect(
            self.actions.toggle_rating_filter_mode
        )
        self.toolbar.favorite_only_checkbox.stateChanged.connect(
            self.actions.apply_filter_and_sort
        )
        self.toolbar.update_required_only_checkbox.stateChanged.connect(
            self.actions.apply_filter_and_sort
        )
        self.toolbar.unknown_only_checkbox.stateChanged.connect(
            self.actions.apply_filter_and_sort
        )
        self.toolbar.unrated_only_checkbox.stateChanged.connect(
            self.actions.apply_filter_and_sort
        )
        self.toolbar.reset_filter_button.clicked.connect(
            self.actions.reset_filters
        )
        self.toolbar.reset_sort_button.clicked.connect(
            self.actions.reset_sort
        )

        self.toolbar.rating_toggle_button.clicked.connect(
            self.actions.toggle_rating_display
        )
        self.toolbar.refresh_button.clicked.connect(
            self.actions.load_artists
        )
        self.toolbar.restore_deleted_button.clicked.connect(
            self.actions.handle_restore_deleted_artists
        )

        self.artist_table.artist_selected.connect(
            self.artist_selected.emit
        )
        self.artist_table.sort_requested.connect(
            self.actions.handle_sort_requested
        )
        self.artist_table.favorite_toggled.connect(
            self.actions.handle_favorite_toggled
        )
        self.artist_table.rating_changed.connect(
            self.actions.handle_rating_changed
        )
        self.artist_table.context_rating_requested.connect(
            self.actions.handle_rating_change_for_artist_ids
        )
        self.artist_table.context_favorite_requested.connect(
            self.actions.handle_favorite_state_for_artist_ids
        )
        self.artist_table.context_delete_requested.connect(
            self.actions.handle_delete_for_artist_ids
        )

    def load_artists(self):
        self.actions.load_artists()

    def select_artist_ids(
        self,
        artist_ids: list[int],
    ):
        self.actions.load_artists()
        self.artist_table.select_artist_ids(artist_ids)
        self.artist_table.setFocus()
