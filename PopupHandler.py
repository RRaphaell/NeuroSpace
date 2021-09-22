from PyQt5.QtWidgets import QMessageBox


class PopupHandler:
    def __init__(self, ui_main) -> None:
        self._ui_main = ui_main

    def warning_popup(self, title, text):
        QMessageBox.critical(self._ui_main, str(title), str(text))
