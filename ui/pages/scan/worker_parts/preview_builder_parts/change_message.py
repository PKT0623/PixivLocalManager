class PreviewChangeMessageMixin:
    def _build_preview_change_message(
        self,
        existing_artist: dict,
        update_data: dict,
    ) -> str:
        messages = []

        change_targets = [
            ("작가명", "artist_name", self._format_text_change_value),
            ("폴더 경로", "folder_path", self._format_text_change_value),
            (
                "작품 수",
                "folder_artwork_count",
                self._format_number_change_value,
            ),
            (
                "파일 수",
                "folder_file_count",
                self._format_number_change_value,
            ),
            (
                "폴더 크기",
                "folder_size_bytes",
                self._format_size_change_value,
            ),
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

    def _append_non_artwork_message(
        self,
        message: str,
        scan_result,
    ) -> str:
        summary_text = getattr(
            scan_result,
            "non_artwork_summary_text",
            "",
        )

        if (
            not summary_text
            or summary_text == "비작품 파일 없음"
        ):
            return message

        return f"{message} / {summary_text}"
