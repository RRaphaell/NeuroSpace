from PyQt5 import QtWidgets
from Widgets.BinWidget import BinWidget
from Widgets.default_widgets import line_edit_with_label


class StimulusActionWidget(BinWidget):
    def __init__(self):
        super().__init__()

        self.pre = None
        self.post = None
        self.bin_width = None
        self.tabs.setTabText(1, "Stimulus Action")

    def _create_bin_group(self):
        group_box = QtWidgets.QGroupBox("Stimulus Action")
        with open("styles/style.qss", "r") as file:
            group_box.setStyleSheet(file.read())
        group_box_layout = QtWidgets.QHBoxLayout()

        self.pre, pre_label = line_edit_with_label("Pre", "Select time parameter")
        self.post, post_label = line_edit_with_label("Post", "Select time parameter")
        self.bin_width, bin_number_label = line_edit_with_label("Bin width", "Select Bin range")

        group_box_layout.addWidget(pre_label)
        group_box_layout.addWidget(self.pre)
        group_box_layout.addWidget(post_label)
        group_box_layout.addWidget(self.post)
        group_box_layout.addWidget(bin_number_label)
        group_box_layout.addWidget(self.bin_width)
        group_box.setLayout(group_box_layout)
        return group_box
