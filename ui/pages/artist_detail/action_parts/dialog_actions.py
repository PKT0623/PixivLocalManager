from PySide6.QtWidgets import QMessageBox


class ArtistDialogActions:
    def show_information(self, title: str, message: str):
        message_box = QMessageBox(self.page)
        message_box.setIcon(QMessageBox.NoIcon)
        message_box.setWindowTitle(title)
        message_box.setText(message)
        message_box.setStandardButtons(QMessageBox.Ok)
        message_box.exec()

    def show_warning(self, title: str, message: str):
        message_box = QMessageBox(self.page)
        message_box.setIcon(QMessageBox.NoIcon)
        message_box.setWindowTitle(title)
        message_box.setText(message)
        message_box.setStandardButtons(QMessageBox.Ok)
        message_box.exec()


    def show_status_message(self, message: str):
        self.page.show_status_message(message)
