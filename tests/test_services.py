from pathlib import Path
from app.services.scan import FolderScanService
from app.services.artwork_status_service import ArtworkStatusService
from app.services.artist import ArtistService
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

    assert result.status == "need_update"
    assert result.local_count == 2
    assert result.pixiv_count == 3
    assert result.missing_count == 1
    assert result.missing_ids == ["99999"]


def test_artist_create():
    test_artist_folder = Path("./test_data/test_artist-999999")

    test_artist_folder.mkdir(
        parents=True,
        exist_ok=True,
    )

    test_image = test_artist_folder / "123456789_p0.png"

    if not test_image.exists():
        test_image.write_bytes(b"test")

    service = ArtistService()

    artist_id = service.create_artist(
        folder_path=str(test_artist_folder),
        rating=3,
        memo="test",
    )

    artist = service.get_artist(artist_id)

    assert artist is not None
    assert artist["pixiv_id"] == "999999"
    assert artist["rating"] == 3
    assert artist["memo"] == "test"


def test_settings():
    service = SettingsService()

    service.set_setting("theme", "dark")
    value = service.get_setting("theme")

    assert value == "dark"

# 테스트 코드 pytest -s
