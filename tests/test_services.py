from app.services.folder_scan_service import FolderScanService
from app.services.artwork_status_service import ArtworkStatusService
from app.services.artist_service import ArtistService
from app.services.settings_service import SettingsService


def test_folder_scan():
    service = FolderScanService()

    result = service.scan_folder("./test_data")

    assert result.folder_file_count >= 0
    assert result.artist_name is not None


def test_artwork_status():
    service = ArtworkStatusService()

    result = service.calculate_status(
        "12345,67890",
        "12345,67890,99999",
    )

    assert result.status in [
        "up_to_date",
        "outdated",
        "unknown",
    ]


def test_artist_create():
    service = ArtistService()

    artist = service.create_artist(
        folder_path="./test_data",
        rating=3,
        memo="test",
    )

    assert artist is not None


def test_settings():
    service = SettingsService()

    service.set_setting("theme", "dark")
    value = service.get_setting("theme")

    assert value == "dark"

# 테스트 코드 pytest -s
