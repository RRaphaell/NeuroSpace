from Widgets.WaveformWidget import WaveformWidget
from PyQt5 import QtWidgets
from Widgets.default_widgets import line_edit_with_label, create_threshold_widgets
from Widgets.default_widgets import merge_widgets


class SpikeWidget(WaveformWidget):
    def __init__(self):
        super().__init__(title="Spike", stimulus_option=True)

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
            self.tabs.setStyleSheet(file.read())

        self.tabs.addTab(self.tab1, "General")
        self.tabs.addTab(self.tab2, "Spikes")

    def _create_spike_tab(self):
        layout = QtWidgets.QGridLayout()
        widget = QtWidgets.QWidget()

        (self.spike_dead_time, self.spike_threshold_from,
         self.spike_threshold_to, self.spike_group_box) = SpikeWidget._create_spike_or_stimulus_group("Spike")

        (self.stimulus_dead_time, self.stimulus_threshold_from,
         self.stimulus_threshold_to, self.stimulus_group_box) = SpikeWidget._create_spike_or_stimulus_group("Stimulus")
        self.stimulus_group_box.setDisabled(True)

        burst_group_box = self._create_burst_group()

        spacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        layout.addWidget(self.spike_group_box, 0, 0, 1, 1)
        layout.addWidget(self.stimulus_group_box, 0, 1, 1, 1)
        layout.addWidget(burst_group_box, 1, 0, 1, 2)
        layout.addItem(spacer, 3, 0, 1, 2)
        widget.setLayout(layout)
        return widget

    @staticmethod
    def _create_spike_or_stimulus_group(title):
        group_box = QtWidgets.QGroupBox(title)
        with open("styles/style.qss", "r") as file:
            group_box.setStyleSheet(file.read())
        group_box_layout = QtWidgets.QGridLayout()

        line_edit, label = line_edit_with_label("Dead time", "Select Dead Time", "")
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(label)
        layout.addWidget(line_edit)
        widget.setLayout(layout)

        threshold_from, threshold_to, threshold_widget = create_threshold_widgets()

        spacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        group_box_layout.addWidget(widget, 0, 0, 1, 2)
        group_box_layout.addItem(spacer, 0, 2, 1, 1)
        group_box_layout.addWidget(threshold_widget, 2, 0, 1, 4)
        group_box.setLayout(group_box_layout)
        return line_edit, threshold_from, threshold_to, group_box

    def _create_burst_group(self):
        group_box = QtWidgets.QGroupBox("Burst")
        group_box.setCheckable(True)
        with open("styles/style.qss", "r") as file:
            group_box.setStyleSheet(file.read())
        group_box_layout = QtWidgets.QGridLayout()

        self.burst_max_start, start_label = line_edit_with_label("Max Start", "Select burst parameter", "")
        self.burst_max_end, end_label = line_edit_with_label("Max End", "Select burst parameter", "")
        self.burst_betw, between_label = line_edit_with_label("Min Between", "Select burst parameter", "")
        self.burst_dur, duration_label = line_edit_with_label("Min Duration", "Select burst parameter", "")
        self.burst_numb, numb_label = line_edit_with_label("Min Number Spike", "Select burst parameter", "")

        start_end = merge_widgets(start_label, self.burst_max_start, end_label, self.burst_max_end)
        between_dur_number = merge_widgets(between_label, self.burst_betw, duration_label,
                                           self.burst_dur, numb_label, self.burst_numb)

        spacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        group_box_layout.addWidget(start_end, 0, 0, 1, 2)
        group_box_layout.addItem(spacer, 0, 1, 1, 1)
        group_box_layout.addWidget(between_dur_number, 1, 0, 1, 3)
        group_box.setLayout(group_box_layout)
        return group_box
