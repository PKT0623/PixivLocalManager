class FollowSaveHandlerMixin:
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
