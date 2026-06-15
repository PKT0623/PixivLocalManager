from pathlib import Path


class FolderScanner:
    IMAGE_EXTENSIONS = {
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".webp",
        ".bmp",
    }

    def find_artist_folders(
        self,
        root_folder: Path,
        max_depth: int = 3,
    ) -> list[Path]:
        folders = []

        def walk(current_folder: Path, depth: int):
            if depth > max_depth:
                return

            try:
                child_folders = [
                    path
                    for path in current_folder.iterdir()
                    if path.is_dir()
                ]
            except OSError:
                return

            for child_folder in child_folders:
                folders.append(child_folder)
                walk(child_folder, depth + 1)

        walk(root_folder, 1)

        return folders

    def has_image_files(
        self,
        folder_path: Path,
    ) -> bool:
        try:
            for file_path in folder_path.rglob("*"):
                if not file_path.is_file():
                    continue

                if file_path.suffix.lower() in self.IMAGE_EXTENSIONS:
                    return True
        except OSError:
            return False

        return False
