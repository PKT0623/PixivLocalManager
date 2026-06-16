from app.database.artist import ArtistRepository
from app.database.app_setting_repository import AppSettingRepository


def run_test():
    print("=== ArtistRepository 테스트 ===")

    artist_repository = ArtistRepository()

    test_artist = {
        "artist_name": "test_artist",
        "pixiv_id": "12345",
        "folder_path": "./test_data",
        "folder_size_bytes": 1000,
        "folder_file_count": 1,
        "folder_artwork_count": 1,
        "rating": 5,
        "status": "active",
        "memo": "test",
        "local_latest_artwork_ids": "111,222",
        "pixiv_latest_artwork_ids": "",
        "update_status": "ok",
        "last_checked_at": None,
    }

    print("\n[CREATE]")
    artist_id = artist_repository.create_artist(test_artist)
    print("artist_id:", artist_id)

    print("\n[GET BY ID]")
    artist = artist_repository.get_by_id(artist_id)
    print(artist)

    print("\n[GET ALL]")
    artists = artist_repository.get_all()
    print(artists)

    print("\n[UPDATE]")
    test_artist["rating"] = 10
    artist_repository.update_artist(artist_id, test_artist)

    print("\n[DELETE]")
    artist_repository.delete_artist(artist_id)

    print("\n=== SettingsRepository 테스트 ===")

    settings_repository = AppSettingRepository()

    settings_repository.set("theme", "dark")
    print(settings_repository.get("theme"))

    all_settings = settings_repository.get_all()
    print(all_settings)

    settings_repository.delete("theme")


if __name__ == "__main__":
    run_test()

# 테스트 코드 python -m tests.test_database
