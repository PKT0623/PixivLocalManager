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
        total = len(items)

        if total == 0:
            self._emit_direct_progress(
                0,
                0,
                "저장할 신규 항목이 없습니다.",
            )
            return self._build_save_result(0, 0, 0, [], False)

        if self.cancel_requested:
            self._emit_direct_progress(
                0,
                total,
                "가져오기를 취소했습니다.",
            )
            return self._build_save_result(0, 0, 0, [], True)

        self._emit_direct_progress(
            0,
            total,
            "가져오기 저장 준비 중...",
        )

        save_result = service.save_follow_users(items)

        saved_count = save_result.get("saved_count", 0)
        updated_count = save_result.get("updated_count", 0)
        error_count = save_result.get("error_count", 0)
        errors = save_result.get("errors", [])

        processed_count = saved_count + updated_count + error_count

        self._emit_direct_progress(
            processed_count,
            total,
            "가져오기 저장 완료",
        )

        return self._build_save_result(
            total=total,
            saved_count=saved_count + updated_count,
            error_count=error_count,
            errors=errors,
            cancelled=self.cancel_requested,
        )

    def _save_bookmark_items(
        self,
        service: BookmarkService,
        items: list[dict],
    ) -> dict:
        total = len(items)

        if total == 0:
            self._emit_direct_progress(
                0,
                0,
                "저장할 신규 항목이 없습니다.",
            )
            return self._build_save_result(0, 0, 0, [], False)

        if self.cancel_requested:
            self._emit_direct_progress(
                0,
                total,
                "가져오기를 취소했습니다.",
            )
            return self._build_save_result(0, 0, 0, [], True)

        self._emit_direct_progress(
            0,
            total,
            "가져오기 저장 준비 중...",
        )

        save_result = service.save_bookmark_artworks(items)

        saved_count = save_result.get("saved_count", 0)
        updated_count = save_result.get("updated_count", 0)
        error_count = save_result.get("error_count", 0)
        errors = save_result.get("errors", [])

        processed_count = saved_count + updated_count + error_count

        self._emit_direct_progress(
            processed_count,
            total,
            "가져오기 저장 완료",
        )

        return self._build_save_result(
            total=total,
            saved_count=saved_count + updated_count,
            error_count=error_count,
            errors=errors,
            cancelled=self.cancel_requested,
        )
