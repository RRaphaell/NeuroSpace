from PyQt5 import QtWidgets
from Widgets.BinWidget import BinWidget
from Widgets.default_widgets import line_edit_with_label
from Widgets.utils import get_default_params


class StimulusActionWidget(BinWidget):
    def __init__(self, window_description):
        super().__init__(window_description)

        self.tabs.setTabText(1, "Stimulus Action")
        self._set_stimulus_action_default_params()

    def _create_bin_group(self):
        print("create_bin_group")
        group_box = QtWidgets.QGroupBox("Stimulus Action")
        with open("styles/style.qss", "r") as file:
            group_box.setStyleSheet(file.read())
        group_box_layout = QtWidgets.QHBoxLayout()

        self.pre, pre_label = line_edit_with_label("Pre", "Select time parameter")
        self.post, post_label = line_edit_with_label("Post", "Select time parameter")
        self.bin_width, bin_width_label = line_edit_with_label("Bin width", "Select Bin range")

        group_box_layout.addWidget(pre_label)
        group_box_layout.addWidget(self.pre)
        group_box_layout.addWidget(post_label)
        group_box_layout.addWidget(self.post)
        group_box_layout.addWidget(bin_width_label)
        group_box_layout.addWidget(self.bin_width)
        group_box.setLayout(group_box_layout)
        return group_box

    def _set_stimulus_action_default_params(self):
        params = get_default_params()
        for key, value in params["StimulusAction"].items():
            att = getattr(self, str(key), None)
            if att is not None:
                att.setText(value)


