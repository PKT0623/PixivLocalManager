from app.database import FollowUserRepository

from .importer import FollowUserImporter
from .matcher import FollowUserMatcher


class FollowService:
    def __init__(self):
        self.repo = FollowUserRepository()
        self.matcher = FollowUserMatcher()
        self.importer = FollowUserImporter()

    def create_follow_user(
        self,
        follow_user: dict,
        match_local_artist: bool = True,
    ) -> int:
        save_data = dict(follow_user)

        if match_local_artist:
            save_data = self.matcher.match_follow_user(save_data)

        return self.repo.create_follow_user(save_data)

    def upsert_follow_user(
        self,
        follow_user: dict,
        match_local_artist: bool = True,
    ) -> int:
        save_data = dict(follow_user)

        if match_local_artist:
            save_data = self.matcher.match_follow_user(save_data)

        return self.repo.upsert_follow_user(save_data)

    def save_follow_users(
        self,
        follow_users: list[dict],
        match_local_artist: bool = True,
    ) -> dict:
        saved_count = 0
        updated_count = 0
        skipped_count = 0
        error_count = 0
        errors = []

        cleaned_follow_users = []
        existing_ids = self.repo.get_existing_pixiv_user_ids(
            self._extract_pixiv_user_ids(follow_users)
        )

        for follow_user in follow_users:
            pixiv_user_id = str(
                follow_user.get("pixiv_user_id", "") or ""
            ).strip()

            if not pixiv_user_id:
                skipped_count += 1
                continue

            item = dict(follow_user)
            item["pixiv_user_id"] = pixiv_user_id
            cleaned_follow_users.append(item)

        try:
            if match_local_artist:
                artist_map = self.matcher.get_artist_map()
                cleaned_follow_users = self.matcher.match_follow_users(
                    follow_users=cleaned_follow_users,
                    artist_map=artist_map,
                )

            save_result = self.repo.upsert_follow_users(cleaned_follow_users)
            saved_count = save_result["saved_count"]
            updated_count = save_result["updated_count"]
            error_count = save_result["error_count"]
            errors = save_result["errors"]
        except Exception as exc:
            error_count += len(cleaned_follow_users)
            errors.append(
                {
                    "pixiv_user_id": "-",
                    "error": str(exc),
                }
            )

        for follow_user in cleaned_follow_users:
            pixiv_user_id = str(
                follow_user.get("pixiv_user_id", "") or ""
            ).strip()

            if pixiv_user_id and pixiv_user_id not in existing_ids:
                existing_ids.add(pixiv_user_id)

        return {
            "total_count": len(follow_users),
            "saved_count": saved_count,
            "updated_count": updated_count,
            "skipped_count": skipped_count,
            "error_count": error_count,
            "errors": errors,
        }

    def preview_follow_users(
        self,
        follow_users: list[dict],
    ) -> dict:
        return self._build_preview_result(follow_users)

    def preview_txt_ids(
        self,
        file_path: str,
    ) -> dict:
        follow_users = self.importer.parse_txt_file(file_path)

        return self.preview_follow_users(follow_users)

    def preview_csv_ids(
        self,
        file_path: str,
    ) -> dict:
        follow_users = self.importer.parse_csv_file(file_path)

        return self.preview_follow_users(follow_users)

    def import_txt_ids(
        self,
        file_path: str,
        match_local_artist: bool = True,
    ) -> dict:
        follow_users = self.importer.parse_txt_file(file_path)

        return self.import_follow_users(
            follow_users=follow_users,
            match_local_artist=match_local_artist,
        )

    def import_csv_ids(
        self,
        file_path: str,
        match_local_artist: bool = True,
    ) -> dict:
        follow_users = self.importer.parse_csv_file(file_path)

        return self.import_follow_users(
            follow_users=follow_users,
            match_local_artist=match_local_artist,
        )

    def import_follow_users(
        self,
        follow_users: list[dict],
        match_local_artist: bool = True,
    ) -> dict:
        preview = self.preview_follow_users(follow_users)
        save_result = self.save_follow_users(
            follow_users=preview["new_items"],
            match_local_artist=match_local_artist,
        )

        return {
            **preview,
            "save_result": save_result,
        }

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

    def _build_preview_result(
        self,
        follow_users: list[dict],
    ) -> dict:
        seen_ids = set()
        new_items = []
        duplicate_in_file_items = []
        duplicate_existing_items = []
        existing_ids = self.repo.get_existing_pixiv_user_ids(
            self._extract_pixiv_user_ids(follow_users)
        )

        for follow_user in follow_users:
            pixiv_user_id = str(
                follow_user.get("pixiv_user_id", "") or ""
            ).strip()

            if not pixiv_user_id:
                continue

            item = dict(follow_user)
            item["pixiv_user_id"] = pixiv_user_id

            if pixiv_user_id in seen_ids:
                duplicate_in_file_items.append(item)
                continue

            seen_ids.add(pixiv_user_id)

            if pixiv_user_id in existing_ids:
                duplicate_existing_items.append(item)
                continue

            new_items.append(item)

        return {
            "total_count": len(follow_users),
            "new_count": len(new_items),
            "duplicate_in_file_count": len(duplicate_in_file_items),
            "duplicate_existing_count": len(duplicate_existing_items),
            "new_items": new_items,
            "duplicate_in_file_items": duplicate_in_file_items,
            "duplicate_existing_items": duplicate_existing_items,
        }

    def _extract_pixiv_user_ids(
        self,
        follow_users: list[dict],
    ) -> list[str]:
        return [
            str(follow_user.get("pixiv_user_id", "") or "").strip()
            for follow_user in follow_users
            if str(follow_user.get("pixiv_user_id", "") or "").strip()
        ]
