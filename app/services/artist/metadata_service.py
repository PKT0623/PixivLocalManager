from app.database.artist import ArtistRepository
from app.services.artist.validation import validate_artist_ids


class ArtistMetadataService:
    def __init__(self):
        self.repo = ArtistRepository()

    def update_artist_metadata(
        self,
        artist_id: int,
        is_favorite: bool | None = None,
        is_hidden: bool | None = None,
        artist_tags: str | None = None,
    ):
        artist = self.repo.get_by_id(artist_id)

        if artist is None:
            raise ValueError("작가를 찾을 수 없습니다.")

        update_data = dict(artist)

        if is_favorite is not None:
            update_data["is_favorite"] = int(bool(is_favorite))

        if is_hidden is not None:
            update_data["is_hidden"] = int(bool(is_hidden))

        if artist_tags is not None:
            update_data["artist_tags"] = artist_tags.strip()

        return self.repo.update_artist(
            artist_id,
            update_data,
        )

    def update_rating(
        self,
        artist_id: int,
        rating: int,
    ):
        self._validate_rating(rating)

        artist = self.repo.get_by_id(artist_id)

        if artist is None:
            raise ValueError("작가를 찾을 수 없습니다.")

        return self.repo.update_rating(
            artist_id,
            rating,
        )

    def bulk_update_rating(
        self,
        artist_ids: list[int],
        rating: int,
    ):
        validate_artist_ids(artist_ids)
        self._validate_rating(rating)

        return self.repo.bulk_update_rating(
            artist_ids,
            rating,
        )

    def bulk_update_favorite(
        self,
        artist_ids: list[int],
        is_favorite: bool,
    ):
        validate_artist_ids(artist_ids)

        return self.repo.bulk_update_favorite(
            artist_ids,
            is_favorite,
        )

    def bulk_update_hidden(
        self,
        artist_ids: list[int],
        is_hidden: bool,
    ):
        validate_artist_ids(artist_ids)

        return self.repo.bulk_update_hidden(
            artist_ids,
            is_hidden,
        )

    def toggle_favorite(self, artist_id: int):
        artist = self.repo.get_by_id(artist_id)

        if artist is None:
            raise ValueError("작가를 찾을 수 없습니다.")

        current_value = bool(artist.get("is_favorite", 0))

        return self.repo.update_favorite(
            artist_id,
            not current_value,
        )

    def toggle_hidden(self, artist_id: int):
        artist = self.repo.get_by_id(artist_id)

        if artist is None:
            raise ValueError("작가를 찾을 수 없습니다.")

        current_value = bool(artist.get("is_hidden", 0))

        return self.repo.update_hidden(
            artist_id,
            not current_value,
        )

    def update_last_viewed(self, artist_id: int):
        return self.repo.update_last_viewed(
            artist_id,
        )

    def _validate_rating(self, rating: int) -> None:
        if rating < 0 or rating > 10:
            raise ValueError("평점은 0~10 사이여야 합니다.")
