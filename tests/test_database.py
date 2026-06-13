from app.database import (
    AppSettingRepository,
    ArtistRepository,
    initialize_database,
)
from app.models import Artist


def run_test() -> None:
    initialize_database()

    artist_repository = ArtistRepository()
    setting_repository = AppSettingRepository()

    print("=== ArtistRepository 테스트 ===")

    artist = Artist(
        artist_name="테스트 작가",
        pixiv_id="987654321",
        folder_path="D:/Pixiv/테스트 작가",
        folder_size_bytes=1024 * 1024 * 5,
        folder_file_count=25,
        folder_artwork_count=10,
        rating=3,
        status="normal",
        memo="생성 테스트",
        local_latest_artwork_ids='["111", "112", "113"]',
        pixiv_latest_artwork_ids='["211", "212", "213"]',
    )

    artist_id = artist_repository.create(artist)
    print(f"Create 성공: id={artist_id}")

    saved_artist = artist_repository.get_by_id(artist_id)
    print(f"Read 성공: {saved_artist}")

    if saved_artist is not None:
        saved_artist.artist_name = "수정된 테스트 작가"
        saved_artist.folder_size_bytes = 1024 * 1024 * 10
        saved_artist.folder_file_count = 40
        saved_artist.folder_artwork_count = 15
        saved_artist.rating = 5
        saved_artist.status = "favorite"
        saved_artist.memo = "수정 테스트"
        saved_artist.local_latest_artwork_ids = '["121", "122", "123"]'
        saved_artist.pixiv_latest_artwork_ids = '["221", "222", "223"]'

        artist_repository.update(saved_artist)

        updated_artist = artist_repository.get_by_id(artist_id)
        print(f"Update 성공: {updated_artist}")

    artist_repository.delete(artist_id)

    deleted_artist = artist_repository.get_by_id(artist_id)
    print(f"Delete 결과: {deleted_artist}")

    print()
    print("=== AppSettingRepository 테스트 ===")

    setting_repository.set(
        "download_root",
        "D:/Pixiv",
    )

    setting_repository.set(
        "thread_count",
        "4",
    )

    setting_repository.set(
        "theme",
        "dark",
    )

    print(
        "Get 성공:",
        setting_repository.get("download_root"),
    )

    print("Get All 성공:")

    settings = setting_repository.get_all()

    for setting in settings:
        print(setting)

    setting_repository.delete("theme")

    deleted_setting = setting_repository.get("theme")

    print(f"Delete 결과: {deleted_setting}")

    print()
    print("DB 테스트 완료")


if __name__ == "__main__":
    run_test()
