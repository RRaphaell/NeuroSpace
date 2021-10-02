from PyQt5 import QtWidgets
from Widgets.WaveformWidget import WaveformWidget
from Widgets.default_widgets import create_group_dead_time_threshold, line_edit_with_label
from Widgets.utils import merge_widgets, get_default_params


class SpikeTogetherWidget(WaveformWidget):
    def __init__(self):
        super().__init__(title="SpikeTogether", stimulus_option=False)

        self.dead_time = None
        self.threshold_from, self.threshold_to = None, None
        self.pre, self.post = None, None
        self.component_number = None
        self._add_tabs()
        self._set_spiketogether_default_params()
        self.setCentralWidget(self.tabs)

    def _add_tabs(self):
        self.tabs = QtWidgets.QTabWidget()
        self.tab1 = self.widget
        self._extract_btn.setDisabled(True)     # spike together can't have extract function
        self.tab2 = self._create_spiketogether_tab()
        with open("styles/style.qss", "r") as file:
            self.setStyleSheet(file.read())
            self.tabs.setStyleSheet(file.read())

        self.tabs.addTab(self.tab1, "General")
        self.tabs.addTab(self.tab2, "SpikeTogether")

    def _create_spiketogether_tab(self):
        layout = QtWidgets.QGridLayout()
        widget = QtWidgets.QWidget()

        (self.dead_time, self.threshold_from,
         self.threshold_to, self.spike_group_box) = create_group_dead_time_threshold("Spike")
        self.component_number, comp_num_label = line_edit_with_label("Comp num", "Select Component number")
        _widget = merge_widgets(comp_num_label, self.component_number, vertical=False)
        self.spike_group_box.layout().addWidget(_widget, 0, 2, 1, 2)
        pre_post_group = self._create_pre_post_group()

        spacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        layout.addWidget(self.spike_group_box, 0, 0, 1, 1)
        layout.addWidget(pre_post_group, 1, 0, 1, 1)
        layout.addItem(spacer, 2, 0, 1, 1)
        widget.setLayout(layout)
        return widget

    def _create_pre_post_group(self):
        group_box = QtWidgets.QGroupBox("Spike separation params")
        with open("styles/style.qss", "r") as file:
            group_box.setStyleSheet(file.read())
        group_box_layout = QtWidgets.QGridLayout()
        self.pre, pre_label = line_edit_with_label("Pre Spike", "Select time parameter")
        self.post, post_label = line_edit_with_label("Post Spike", "Select time parameter")
        _pre_widget = merge_widgets(pre_label, self.pre, vertical=False)
        _post_widget = merge_widgets(post_label, self.post, vertical=False)

        spacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        group_box_layout.addWidget(_pre_widget, 0, 0, 1, 2)
        group_box_layout.addWidget(_post_widget, 1, 0, 1, 2)
        group_box_layout.addItem(spacer, 0, 2, 1, 1)
        group_box_layout.addItem(spacer, 1, 2, 1, 1)
        group_box.setLayout(group_box_layout)
        return group_box

    def set_plot_func(self, func):
        self._plot_btn.clicked.connect(func)

    def _set_spiketogether_default_params(self):
        params = get_default_params()
        for key, value in params["SpikeTogether"].items():
            att = getattr(self, str(key), None)
            if att is not None:
                att.setText(value)


