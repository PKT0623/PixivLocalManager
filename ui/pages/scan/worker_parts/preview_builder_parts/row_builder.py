from pathlib import Path


class PreviewRowBuilderMixin:
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
            "non_artwork_summary": scan_result.non_artwork_summary,
            "non_artwork_summary_text": (
                scan_result.non_artwork_summary_text
            ),
            "non_artwork_files": scan_result.non_artwork_files,
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
            "non_artwork_summary": {},
            "non_artwork_summary_text": "비작품 파일 없음",
            "non_artwork_files": [],
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
            "non_artwork_summary": {},
            "non_artwork_summary_text": "비작품 파일 없음",
            "non_artwork_files": [],
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
