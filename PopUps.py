from PyQt5.QtWidgets import QMessageBox


class PopUps:
    ui_main = None

    def __init__(self,ui_main) -> None:
        ui_main = ui_main
        
    @staticmethod
    def warning_popup(text, title):
        QMessageBox.critical(PopUps.ui_main, text, title)
