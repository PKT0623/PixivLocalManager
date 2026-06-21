import time

from app.services import BookmarkService, FollowService


class FileImportMixin:
    def _import_follow(self) -> dict:
        service = FollowService()

        if self.file_type == "txt":
            items = service.importer.parse_txt_file(self.file_path)
        else:
            items = service.importer.parse_csv_file(self.file_path)

        preview = service.preview_follow_users(items)
        new_items = preview["new_items"]

        save_result = self._save_follow_items(
            service=service,
            items=new_items,
        )

        return {
            **preview,
            "import_source": "file",
            "target_type": "follow",
            "file_type": self.file_type,
            "save_result": save_result,
            "cancelled": self.cancel_requested,
        }

    def _import_bookmark(self) -> dict:
        service = BookmarkService()

        if self.file_type == "txt":
            items = service.importer.parse_txt_file(self.file_path)
        else:
            items = service.importer.parse_csv_file(self.file_path)

        preview = service.preview_bookmark_artworks(items)
        new_items = preview["new_items"]

        save_result = self._save_bookmark_items(
            service=service,
            items=new_items,
        )

        return {
            **preview,
            "import_source": "file",
            "target_type": "bookmark",
            "file_type": self.file_type,
            "save_result": save_result,
            "cancelled": self.cancel_requested,
        }

    def _save_follow_items(
        self,
        service: FollowService,
        items: list[dict],
    ) -> dict:
        saved_count = 0
        error_count = 0
        errors = []

        total = len(items)
        started_at = time.time()

        if total == 0:
            self._emit_direct_progress(0, 0, "저장할 신규 항목이 없습니다.")
            self.estimated_time_updated.emit("-")
            return self._build_save_result(0, 0, 0, [], False)

        for index, item in enumerate(items, start=1):
            if self.cancel_requested:
                self._emit_direct_progress(
                    index - 1,
                    total,
                    "가져오기를 취소했습니다.",
                )
                break

            try:
                service.upsert_follow_user(item)
                saved_count += 1
            except Exception as error:
                error_count += 1
                errors.append(
                    {
                        "pixiv_user_id": item.get("pixiv_user_id", ""),
                        "error": str(error),
                    }
                )

            self._emit_progress(
                index=index,
                total=total,
                started_at=started_at,
            )

        return self._build_save_result(
            total=total,
            saved_count=saved_count,
            error_count=error_count,
            errors=errors,
            cancelled=self.cancel_requested,
        )

    def _save_bookmark_items(
        self,
        service: BookmarkService,
        items: list[dict],
    ) -> dict:
        saved_count = 0
        error_count = 0
        errors = []

        total = len(items)
        started_at = time.time()

        if total == 0:
            self._emit_direct_progress(0, 0, "저장할 신규 항목이 없습니다.")
            self.estimated_time_updated.emit("-")
            return self._build_save_result(0, 0, 0, [], False)

        for index, item in enumerate(items, start=1):
            if self.cancel_requested:
                self._emit_direct_progress(
                    index - 1,
                    total,
                    "가져오기를 취소했습니다.",
                )
                break

            try:
                service.upsert_bookmark_artwork(item)
                saved_count += 1
            except Exception as error:
                error_count += 1
                errors.append(
                    {
                        "artwork_id": item.get("artwork_id", ""),
                        "error": str(error),
                    }
                )

            self._emit_progress(
                index=index,
                total=total,
                started_at=started_at,
            )

        return self._build_save_result(
            total=total,
            saved_count=saved_count,
            error_count=error_count,
            errors=errors,
            cancelled=self.cancel_requested,
        )
