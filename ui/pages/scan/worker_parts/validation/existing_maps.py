from pathlib import Path


class ExistingMapsMixin:
    def _build_existing_pixiv_id_map(
        self,
        artists: list[dict],
    ) -> dict[str, dict]:
        result = {}

        for artist in artists:
            pixiv_id = str(artist.get("pixiv_id", "") or "").strip()

            if not pixiv_id:
                continue

            result[pixiv_id] = artist

        return result

    def _build_existing_folder_path_map(
        self,
        artists: list[dict],
    ) -> dict[str, dict]:
        result = {}

        for artist in artists:
            folder_path = str(artist.get("folder_path", "") or "").strip()

            if not folder_path:
                continue

            result[str(Path(folder_path).resolve()).casefold()] = artist

        return result
