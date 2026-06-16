from pathlib import Path


class PreviewBuilderMixin:
    def _preview_artist_folder(
        self,
        folder_path: Path,
        existing_by_pixiv_id: dict[str, dict],
    ) -> dict:
        scan_result = self.folder_scan_service.scan_folder(str(folder_path))
        pixiv_id = str(scan_result.pixiv_id or "").strip()
        existing_artist = existing_by_pixiv_id.get(pixiv_id)

        if existing_artist is None:
            return self._build_preview_row(
                preview_result="신규 등록 예정",
                can_scan=True,
                scan_result=scan_result,
                existing_artist=None,
                message="새 작가로 등록됩니다.",
            )

        update_status = self.status_service.calculate_status(
            scan_result.local_latest_artwork_ids,
            existing_artist.get("pixiv_latest_artwork_ids", ""),
        )

        update_data = dict(existing_artist)
        update_data["artist_name"] = scan_result.artist_name
        update_data["pixiv_id"] = scan_result.pixiv_id
        update_data["folder_path"] = scan_result.folder_path
        update_data["folder_size_bytes"] = scan_result.folder_size_bytes
        update_data["folder_file_count"] = scan_result.folder_file_count
        update_data["folder_artwork_count"] = scan_result.folder_artwork_count
        update_data["local_latest_artwork_ids"] = (
            scan_result.local_latest_artwork_ids
        )
        update_data["update_status"] = update_status.status

        change_message = self._build_preview_change_message(
            existing_artist,
            update_data,
        )

        if change_message:
            return self._build_preview_row(
                preview_result="업데이트 예정",
                can_scan=True,
                scan_result=scan_result,
                existing_artist=existing_artist,
                message=change_message,
            )

        return self._build_preview_row(
            preview_result="변경 없음 예정",
            can_scan=True,
            scan_result=scan_result,
            existing_artist=existing_artist,
            message="등록된 정보와 변경 사항이 없습니다.",
        )

    def _build_preview_row(
        self,
        preview_result: str,
        can_scan: bool,
        scan_result,
        existing_artist: dict | None,
        message: str,
    ) -> dict:
        return {
            "preview_result": preview_result,
            "can_scan": can_scan,
            "artist_id": (
                existing_artist.get("id")
                if existing_artist is not None
                else None
            ),
            "artist_name": scan_result.artist_name or "-",
            "pixiv_id": scan_result.pixiv_id or "-",
            "artwork_count": scan_result.folder_artwork_count,
            "file_count": scan_result.folder_file_count,
            "folder_path": scan_result.folder_path,
            "message": message,
            "scan_result": scan_result,
        }

    def _build_preview_error_row(
        self,
        row_data: dict,
    ) -> dict:
        return {
            "preview_result": "오류 예상",
            "can_scan": False,
            "artist_id": None,
            "artist_name": row_data.get("artist_name", "-"),
            "pixiv_id": row_data.get("pixiv_id", "-"),
            "artwork_count": "-",
            "file_count": "-",
            "folder_path": row_data.get("folder_path", "-"),
            "message": row_data.get("error_message", "-"),
        }

    def _build_preview_exception_row(
        self,
        folder_path: Path,
        error: Exception,
    ) -> dict:
        return {
            "preview_result": "오류 예상",
            "can_scan": False,
            "artist_id": None,
            "artist_name": folder_path.name,
            "pixiv_id": "-",
            "artwork_count": "-",
            "file_count": "-",
            "folder_path": str(folder_path),
            "message": str(error),
        }

    def _strip_preview_runtime_objects(
        self,
        rows: list[dict],
    ) -> list[dict]:
        result = []

        for row in rows:
            item = dict(row)
            item.pop("scan_result", None)
            result.append(item)

        return result

    def _build_preview_change_message(
        self,
        existing_artist: dict,
        update_data: dict,
    ) -> str:
        messages = []

        change_targets = [
            ("작가명", "artist_name", self._format_text_change_value),
            ("폴더 경로", "folder_path", self._format_text_change_value),
            ("작품 수", "folder_artwork_count", self._format_number_change_value),
            ("파일 수", "folder_file_count", self._format_number_change_value),
            ("폴더 크기", "folder_size_bytes", self._format_size_change_value),
            ("업데이트 상태", "update_status", self._format_text_change_value),
        ]

        for label, field_name, formatter in change_targets:
            old_value = existing_artist.get(field_name)
            new_value = update_data.get(field_name)

            if not self._is_value_changed(old_value, new_value):
                continue

            messages.append(
                f"{label} {formatter(old_value)} → {formatter(new_value)}"
            )

        old_artwork_ids = str(
            existing_artist.get("local_latest_artwork_ids", "") or ""
        )
        new_artwork_ids = str(
            update_data.get("local_latest_artwork_ids", "") or ""
        )

        if self._is_value_changed(old_artwork_ids, new_artwork_ids):
            messages.extend(
                self._build_artwork_id_change_messages(
                    old_artwork_ids,
                    new_artwork_ids,
                )
            )

        return " / ".join(messages)

    def _build_artwork_id_change_messages(
        self,
        old_value: str,
        new_value: str,
    ) -> list[str]:
        old_ids = self._split_artwork_ids(old_value)
        new_ids = self._split_artwork_ids(new_value)

        added_ids = [
            artwork_id
            for artwork_id in new_ids
            if artwork_id not in old_ids
        ]
        removed_ids = [
            artwork_id
            for artwork_id in old_ids
            if artwork_id not in new_ids
        ]

        messages = []

        if added_ids:
            messages.append(
                "신규 작품 ID "
                + ", ".join(added_ids[:5])
                + self._format_overflow_count(len(added_ids), 5)
            )

        if removed_ids:
            messages.append(
                "제외된 작품 ID "
                + ", ".join(removed_ids[:5])
                + self._format_overflow_count(len(removed_ids), 5)
            )

        if not messages:
            messages.append("최신 작품 ID 순서 변경")

        return messages

    def _split_artwork_ids(
        self,
        value: str,
    ) -> list[str]:
        return [
            item.strip()
            for item in str(value or "").split(",")
            if item.strip()
        ]

    def _format_overflow_count(
        self,
        total_count: int,
        display_limit: int,
    ) -> str:
        remain_count = int(total_count or 0) - int(display_limit or 0)

        if remain_count <= 0:
            return ""

        return f" 외 {remain_count}개"

    def _is_value_changed(
        self,
        old_value,
        new_value,
    ) -> bool:
        return str(old_value or "") != str(new_value or "")

    def _format_text_change_value(
        self,
        value,
    ) -> str:
        value = str(value or "").strip()

        if not value:
            return "-"

        return value

    def _format_number_change_value(
        self,
        value,
    ) -> str:
        try:
            return str(int(value or 0))
        except (TypeError, ValueError):
            return "0"

    def _format_size_change_value(
        self,
        value,
    ) -> str:
        try:
            size = int(value or 0)
        except (TypeError, ValueError):
            size = 0

        if size >= 1024 * 1024 * 1024:
            return f"{size / (1024 * 1024 * 1024):.2f} GB"

        if size >= 1024 * 1024:
            return f"{size / (1024 * 1024):.2f} MB"

        if size >= 1024:
            return f"{size / 1024:.2f} KB"

        return f"{size} B"
