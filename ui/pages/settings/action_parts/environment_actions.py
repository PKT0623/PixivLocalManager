from pathlib import Path


class SettingsEnvironmentActions:
    def refresh_environment_info(self):
        width = self.page.settings_service.get_setting("window_width")
        height = self.page.settings_service.get_setting("window_height")
        x = self.page.settings_service.get_setting("window_x")
        y = self.page.settings_service.get_setting("window_y")

        window_size = "-"

        if width and height:
            window_size = f"{width} x {height}"

        window_position = "-"

        if x and y:
            window_position = f"X: {x}, Y: {y}"

        info = {
            "window_size": window_size,
            "window_position": window_position,
            "last_backup_folder": self._get_folder_label(
                "last_settings_backup_folder"
            ),
            "last_restore_folder": self._get_folder_label(
                "last_settings_restore_folder"
            ),
            "last_export_folder": self._get_folder_label(
                "last_export_folder"
            ),
        }

        self.page.settings_management_section.update_environment_info(info)

    def _get_initial_folder(
        self,
        key: str,
        fallback,
    ) -> Path:
        saved_folder = self.page.settings_service.get_setting(key)

        if saved_folder and Path(saved_folder).exists():
            return Path(saved_folder)

        return Path(fallback)

    def _save_last_folder(
        self,
        key: str,
        file_path: str,
    ):
        folder_path = Path(file_path).parent

        self.page.settings_service.set_setting(
            key,
            str(folder_path),
        )

    def _get_folder_label(
        self,
        key: str,
    ) -> str:
        folder = self.page.settings_service.get_setting(key)

        if not folder:
            return "-"

        return str(folder)
