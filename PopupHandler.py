from PyQt5.QtWidgets import QMessageBox


class PopupHandler:
    """
    PopupHandler class display's warning and information popup's according to demand

    Args:
        ui_main ('UI.NeuroSpace'): the main UI object of function
    """
    def __init__(self, ui_main) -> None:
        self._ui_main = ui_main

    def warning_popup(self, title, text):
        """
        warning_popup displays warnings during errors (especially when some exception happens)

        Args:
            title (str): the title of warning pop-up
            text (str): the text body of future warning
        """
        QMessageBox.critical(self._ui_main, str(title), str(text))

    def info_popup(self, title, text):
        """
        info_popup displays some information for user

        Args:
            title (str): the short title of an information
            text (str): the actual information
        """
        QMessageBox.information(self._ui_main, str(title), str(text))
