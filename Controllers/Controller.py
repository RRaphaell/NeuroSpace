from utils import get_default_widget


class Controller:
    def __init__(self, file, key, open_window_dict, mdi, parameters_dock, popup_handler, dialog, view):
        self.file = file
        self._key = key
        self.open_window_dict = open_window_dict
        self.parameters_dock = parameters_dock
        self._dialog = dialog
        self.mdi = mdi
        self.popup_handler = popup_handler

        self.view = view

    def _enable_stimulus_if_checked(self):
        if len(self.view.channel_widget.marked_stimulus_channels):
            self.view.stimulus_group_box.setEnabled(True)
        else:
            self.view.stimulus_group_box.setDisabled(True)

    def _remove_me(self):
        del self.open_window_dict[self._key]
        self.parameters_dock.setWidget(get_default_widget())
