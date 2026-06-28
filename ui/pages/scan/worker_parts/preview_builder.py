from pathlib import Path

from .preview_builder_parts import (
    PreviewChangeMessageMixin,
    PreviewFormatterMixin,
    PreviewRowBuilderMixin,
)


class PreviewBuilderMixin(
    PreviewRowBuilderMixin,
    PreviewChangeMessageMixin,
    PreviewFormatterMixin,
):
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
                message=self._append_non_artwork_message(
                    "새 작가로 등록됩니다.",
                    scan_result,
                ),
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
                message=self._append_non_artwork_message(
                    change_message,
                    scan_result,
                ),
            )

        return self._build_preview_row(
            preview_result="변경 없음 예정",
            can_scan=True,
            scan_result=scan_result,
            existing_artist=existing_artist,
            message=self._append_non_artwork_message(
                "등록된 정보와 변경 사항이 없습니다.",
                scan_result,
            ),
        )
