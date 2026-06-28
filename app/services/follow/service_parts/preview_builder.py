class FollowPreviewBuilderMixin:
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
