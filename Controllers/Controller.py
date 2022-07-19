from utils import get_default_widget


class Controller:
    """
    Controller class and its child classes are for UI-back relationships

    Attributes:
              file (McsPy.McsData.RawData): the main recorded file
              open_window_dict (dict): active windows dict, the key - window id(int),
                                        the value - appropriate window object
              parameters_dock (QtWidgets.QDockWidget):
              mdi (QtWidgets.QMdiArea): the area where can be window objects displayed
              popup_handler (function): this function is to display corresponding popups
              view (Widgets.WaveformWidget.WaveformWidget):

    Args:
              file (McsPy.McsData.RawData): the main recorded file
              key (int): window id
              open_window_dict (dict): active windows dict, the key - window id(int),
                                        the value - appropriate window object
              mdi (QtWidgets.QMdiArea): the area where can be window objects displayed
              parameters_dock ('PyQt5.QtWidgets.QDockWidget):
              popup_handler (function): this function is to display corresponding popups
              dialog (PyQt5.QtWidgets.QDialog): dialog window for choosing channels, time and etc..
              view (Widgets.WaveformWidget.WaveformWidget):

    """
    def __init__(self, file, key, open_window_dict, mdi, parameters_dock, popup_handler, dialog, view):
        self.file = file
        self._key = key
        self.open_window_dict = open_window_dict
        self.parameters_dock = parameters_dock
        self._dialog = dialog
        self.mdi = mdi
        self.popup_handler = popup_handler

        self.view = view

    def _enable_stimulus_if_checked(self) -> None:
        """
        This function enables stimulus channel on double click
        """
        if len(self.view.channel_widget.marked_stimulus_channels):
            self.view.stimulus_group_box.setEnabled(True)
        else:
            self.view.stimulus_group_box.setDisabled(True)

    def _remove_me(self):
        """
        This function removes existing opened window object
        """
        del self.open_window_dict[self._key]
        self.parameters_dock.setWidget(get_default_widget())
