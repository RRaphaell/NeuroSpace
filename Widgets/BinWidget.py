from Widgets.WaveformWidget import WaveformWidget
from Widgets.default_widgets import create_group_dead_time_threshold, line_edit_with_label
from PyQt5 import QtWidgets

from Widgets.utils import get_default_params


class BinWidget(WaveformWidget):
    def __init__(self):
        super().__init__(title="Bin", stimulus_option=True)

        self.plot_func = None

        self._add_tabs()
        self._set_bin_default_params()
        self.setCentralWidget(self.tabs)

    def _add_tabs(self):
        self.tabs = QtWidgets.QTabWidget()
        self.tab1 = self.widget
        self.tab2 = self._create_bin_tab()
        with open("styles/style.qss", "r") as file:
            self.setStyleSheet(file.read())
            self.tabs.setStyleSheet(file.read())

        self.tabs.addTab(self.tab1, "General")
        self.tabs.addTab(self.tab2, "Bin")

    def _create_bin_tab(self):
        layout = QtWidgets.QGridLayout()
        widget = QtWidgets.QWidget()

        (self.spike_dead_time, self.spike_threshold_from,
         self.spike_threshold_to, self.spike_group_box) = create_group_dead_time_threshold("Spike")

        (self.stimulus_dead_time, self.stimulus_threshold_from,
         self.stimulus_threshold_to, self.stimulus_group_box) = create_group_dead_time_threshold("Stimulus")
        self.stimulus_group_box.setDisabled(True)

        bin_group_box = self._create_bin_group()

        spacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        layout.addWidget(self.spike_group_box, 0, 0, 1, 1)
        layout.addWidget(self.stimulus_group_box, 0, 1, 1, 1)
        layout.addWidget(bin_group_box, 1, 0, 1, 1)
        layout.addItem(spacer, 3, 0, 1, 2)
        widget.setLayout(layout)
        return widget

    def _create_bin_group(self):
        group_box = QtWidgets.QGroupBox("Bin")
        with open("styles/style.qss", "r") as file:
            group_box.setStyleSheet(file.read())
        group_box_layout = QtWidgets.QHBoxLayout()

        self.bin_width, bin_width_label = line_edit_with_label("Bin range", "Select Bin range")

        group_box_layout.addWidget(bin_width_label)
        group_box_layout.addWidget(self.bin_width)
        group_box.setLayout(group_box_layout)
        return group_box
    
    def set_extract_func(self, func):
        self._extract_btn.clicked.connect(func)

    @property
    def plot_func(self):
        return self._plot_func

    @plot_func.setter
    def plot_func(self, func):
        self._plot_func = func

    def _set_bin_default_params(self):
        params = get_default_params()
        for key, value in params["Bin"].items():
            att = getattr(self, str(key), None)
            if att is not None:
                att.setText(value)
