from Widgets.WaveformWidget import WaveformWidget
from PyQt5 import QtWidgets
from Widgets.default_widgets import line_edit_with_label, create_threshold_widgets


class SpikeWidget(WaveformWidget):
    def __init__(self):
        super().__init__("Spike")

        self.spike_dead_time, self.stimulus_dead_time = None, None
        self.spike_threshold_from, self.stimulus_threshold_from = None, None
        self.spike_threshold_to, self.stimulus_threshold_to = None, None
        self.burst_max_start, self.burst_max_end = None, None
        self.burst_betw, self.burst_dur, self.burst_numb = None, None, None

        self._add_tabs()
        self.setCentralWidget(self.tabs)

    def _add_tabs(self):
        self.tabs = QtWidgets.QTabWidget()
        self.tab1 = self.widget
        self.tab2 = self._create_spike_tab()
        with open("styles/style.qss", "r") as file:
            self.setStyleSheet(file.read())

        self.tabs.addTab(self.tab1, "General")
        self.tabs.addTab(self.tab2, "Spikes")

    def _create_spike_tab(self):
        layout = QtWidgets.QGridLayout()
        widget = QtWidgets.QWidget()

        (self.spike_dead_time, self.spike_threshold_from,
         self.spike_threshold_to, spike_group_box) = SpikeWidget._create_spike_or_stimulus_group("Spike")

        (self.stimulus_dead_time, self.stimulus_threshold_from,
         self.stimulus_threshold_to, stimulus_group_box) = SpikeWidget._create_spike_or_stimulus_group("Stimulus")

        layout.addWidget(spike_group_box, 0, 0, 1, 1)
        layout.addWidget(stimulus_group_box, 0, 1, 1, 1)
        widget.setLayout(layout)
        return widget

    @staticmethod
    def _create_spike_or_stimulus_group(title):
        group_box = QtWidgets.QGroupBox(title)
        with open("styles/style.qss", "r") as file:
            group_box.setStyleSheet(file.read())

        group_box_layout = QtWidgets.QGridLayout()

        line_edit, label = line_edit_with_label("Dead time", "Select Dead Time", "")
        line_edit.setMaximumWidth(80)
        threshold_from, threshold_to, threshold_widget = create_threshold_widgets()

        spacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)

        group_box_layout.addWidget(line_edit, 3, 1, 1, 1)
        group_box_layout.addWidget(label, 3, 0, 1, 1)
        group_box_layout.addItem(spacer, 3, 2, 1, 1)
        group_box_layout.addWidget(threshold_widget, 4, 0, 1, 4)
        group_box.setLayout(group_box_layout)
        return line_edit, threshold_from, threshold_to, group_box

    @staticmethod
    def _create_burst_group(self):
        pass

