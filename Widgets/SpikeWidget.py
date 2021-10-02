from Widgets.WaveformWidget import WaveformWidget
from PyQt5 import QtWidgets
from Widgets.default_widgets import (line_edit_with_label,
                                     create_group_dead_time_threshold,
                                     merge_widgets)
from Widgets.utils import get_default_params, clear_qlines


class SpikeWidget(WaveformWidget):
    def __init__(self, window_description):
        super().__init__(window_description, title="Spike", stimulus_option=True)

        self.spike_dead_time, self.stimulus_dead_time = None, None
        self.spike_threshold_from, self.stimulus_threshold_from = None, None
        self.spike_threshold_to, self.stimulus_threshold_to = None, None
        self.burst_max_start, self.burst_max_end = None, None
        self.burst_between, self.burst_duration, self.burst_number = None, None, None
        self.pre, self.post, self.component_number = None, None, None

        self._add_tabs()
        self._set_spike_default_params()
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
         self.spike_threshold_to, self.spike_group_box) = create_group_dead_time_threshold("Spike")

        (self.stimulus_dead_time, self.stimulus_threshold_from,
         self.stimulus_threshold_to, self.stimulus_group_box) = create_group_dead_time_threshold("Stimulus")

        self.burst_group_box = self._create_burst_group()
        self.burst_group_box.toggled.connect(lambda: clear_qlines(self.burst_max_start, self.burst_max_end,
                                                                  self.burst_between, self.burst_duration,
                                                                  self.burst_number))
        self.pca_group_box = self._create_pca_tab()
        self.pca_group_box.toggled.connect(lambda: clear_qlines(self.pre, self.post, self.component_number))

        spacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        layout.addWidget(self.spike_group_box, 0, 0, 1, 1)
        layout.addWidget(self.stimulus_group_box, 1, 0, 1, 1)
        layout.addWidget(self.burst_group_box, 2, 0, 1, 1)
        layout.addWidget(self.pca_group_box, 3, 0, 1, 1)
        layout.addItem(spacer, 4, 0, 1, 1)
        widget.setLayout(layout)
        return widget

    def _create_pca_tab(self):
        group_box = QtWidgets.QGroupBox("Spike separation params")
        group_box.setCheckable(True)
        with open("styles/style.qss", "r") as file:
            group_box.setStyleSheet(file.read())

        group_box_layout = QtWidgets.QGridLayout()
        self.pre, pre_label = line_edit_with_label("Pre", "Select time parameter")
        self.post, post_label = line_edit_with_label("Post", "Select time parameter")
        self.component_number, spike_comp_num_label = line_edit_with_label("Comp num", "Select Component number")
        spacer = QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)

        pre_post_widget = merge_widgets(pre_label, self.pre, spacer, post_label, self.post, spacer, spike_comp_num_label, vertical=False)
        component_number_widget = merge_widgets(spike_comp_num_label, self.component_number, vertical=False)

        group_box_layout.addWidget(pre_post_widget, 0, 0, 1, 1)
        group_box_layout.addWidget(component_number_widget, 1, 0, 1, 1)
        group_box.setLayout(group_box_layout)
        return group_box

    def _create_burst_group(self):
        group_box = QtWidgets.QGroupBox("Burst")
        group_box.setCheckable(True)
        with open("styles/style.qss", "r") as file:
            group_box.setStyleSheet(file.read())
        group_box_layout = QtWidgets.QGridLayout()

        self.burst_max_start, start_label = line_edit_with_label("Max Start", "Select burst parameter")
        self.burst_max_end, end_label = line_edit_with_label("Max End", "Select burst parameter")
        self.burst_between, between_label = line_edit_with_label("Min Between", "Select burst parameter")
        self.burst_duration, duration_label = line_edit_with_label("Min Duration", "Select burst parameter")
        self.burst_number, numb_label = line_edit_with_label("Min Number Spike", "Select burst parameter")

        start_end_widget = merge_widgets(start_label, self.burst_max_start, end_label, self.burst_max_end)
        between_dur_widget = merge_widgets(between_label, self.burst_between, duration_label, self.burst_duration)
        number_widget = merge_widgets(numb_label, self.burst_number)

        spacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        group_box_layout.addWidget(start_end_widget, 0, 0, 1, 1)
        group_box_layout.addWidget(between_dur_widget, 1, 0, 1, 1)
        group_box_layout.addWidget(number_widget, 2, 0, 1, 1)
        group_box.setLayout(group_box_layout)
        return group_box

    def set_plot_func(self, func):
        self._plot_btn.clicked.connect(func)
    
    def set_extract_func(self, func):
        self._extract_btn.clicked.connect(func)

    def _set_spike_default_params(self):
        params = get_default_params()
        for key, value in params["Spike"].items():
            att = getattr(self, str(key), None)
            if att is not None:
                att.setText(value)
