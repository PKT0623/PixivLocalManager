from app.database import FollowUserRepository

from app.services.follow.importer import FollowUserImporter
from app.services.follow.matcher import FollowUserMatcher

from .preview_builder import FollowPreviewBuilderMixin
from .save_handler import FollowSaveHandlerMixin


class FollowService(
    FollowPreviewBuilderMixin,
    FollowSaveHandlerMixin,
):
    def __init__(self):
        self.repo = FollowUserRepository()
        self.matcher = FollowUserMatcher()
        self.importer = FollowUserImporter()

    def get_follow_user(
        self,
        follow_user_id: int,
    ):
        return self.repo.get_by_id(follow_user_id)

    def get_follow_user_by_pixiv_id(
        self,
        pixiv_user_id: str,
    ):
        return self.repo.get_by_pixiv_user_id(pixiv_user_id)

    def get_all_follow_users(self) -> list[dict]:
        return self.repo.get_all()

    def get_unmatched_follow_users(self) -> list[dict]:
        return self.repo.get_unmatched()

    def update_follow_user(
        self,
        follow_user_id: int,
        follow_user: dict,
        match_local_artist: bool = True,
    ) -> None:
        update_data = dict(follow_user)

        if match_local_artist:
            update_data = self.matcher.match_follow_user(update_data)

        return self.repo.update_follow_user(
            follow_user_id,
            update_data,
        )

    def match_all_follow_users(self) -> dict:
        return self.matcher.match_all()

    def toggle_favorite(
        self,
        follow_user_id: int,
    ) -> None:
        follow_user = self.repo.get_by_id(follow_user_id)

        if follow_user is None:
            raise ValueError("팔로우 유저를 찾을 수 없습니다.")

        current_value = bool(follow_user.get("is_favorite", 0))

        return self.repo.update_favorite(
            follow_user_id,
            not current_value,
        )

    def toggle_hidden(
        self,
        follow_user_id: int,
    ) -> None:
        follow_user = self.repo.get_by_id(follow_user_id)

        if follow_user is None:
            raise ValueError("팔로우 유저를 찾을 수 없습니다.")

        current_value = bool(follow_user.get("is_hidden", 0))

        return self.repo.update_hidden(
            follow_user_id,
            not current_value,
        )

    def delete_follow_user(
        self,
        follow_user_id: int,
    ) -> None:
        return self.repo.delete_follow_user(follow_user_id)

    def delete_all_follow_users(self) -> None:
        return self.repo.delete_all()
