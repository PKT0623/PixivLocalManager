from pathlib import Path


class FolderScanner:
    IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}

    def find_artist_folders(
        self,
        root_folder: Path,
        max_depth: int = 3,
    ) -> list[Path]:
        artist_folders = []

        for folder_path in self.iter_folders(root_folder, max_depth):
            if self.has_image_files(folder_path):
                artist_folders.append(folder_path)

        return sorted(
            set(artist_folders),
            key=lambda path: str(path).lower(),
        )

    def iter_folders(
        self,
        root_folder: Path,
        max_depth: int,
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

        if self.has_image_files(root_folder):
            folders.insert(0, root_folder)

        return folders

    def has_image_files(self, folder_path: Path) -> bool:
        try:
            for file_path in folder_path.iterdir():
                if not file_path.is_file():
                    continue

                if file_path.suffix.lower() in self.IMAGE_EXTENSIONS:
                    return True
        except OSError:
            return False

        return False
