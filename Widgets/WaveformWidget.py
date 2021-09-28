from PyQt5 import QtWidgets, QtGui
from Widgets.utils import move_center, calculate_row_col_adjustment, create_widget_layout, get_default_params
from Widgets.default_widgets import (create_widget_description,
                                     create_time_range_widgets,
                                     create_filter_widgets,
                                     create_plot_extract_buttons)
from Widgets.ChannelIdsWidget import ChannelIdsWidget
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar


class WaveformWidget(QtWidgets.QMainWindow):

    def __init__(self, title="Waveform", stimulus_option=False):
        super().__init__()

        self.plot_widget = None
        self.plot_window = None
        self.canvas = None

        waveform_text = create_widget_description("აღწერა \n აქ შეგიძლიათ აირჩიოთ სხვადასხვა არხი და ააგოთ სიგნალი. ააგოთ როგორც არხების საშუალო ასევე სხვადასხვა არხებიც ცალ-ცალკე")
        self.channel_widget = ChannelIdsWidget(stimulus_option=stimulus_option)
        self.from_s, self.to_s, time_range_widget = create_time_range_widgets()
        self.high_pass, self.low_pass, filter_widget = create_filter_widgets()
        self._plot_btn, self._extract_btn, self.buttons_widget = create_plot_extract_buttons()

        self.widget = create_widget_layout(waveform_text, self.channel_widget,
                                           time_range_widget, filter_widget, self.buttons_widget)

        self._set_waveform_default_params()
        self.setCentralWidget(self.widget)
        self.setWindowTitle(title)
        self.move(move_center(self.frameGeometry()).topLeft())

    def get_path_for_save(self):
        name, _ = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File', options=QtWidgets.QFileDialog.DontUseNativeDialog)
        return name

    def set_plot_func(self, func):
        self._plot_btn.clicked.connect(func)

    def set_extract_func(self, func):
        self._extract_btn.clicked.connect(func)

    def create_plot_widget(self, subplot_num):
        plot_widget = QtWidgets.QWidget()
        n_rows, n_cols = calculate_row_col_adjustment(subplot_num)
        figure, _ = plt.subplots(nrows=n_rows, ncols=n_cols)
        self.canvas = FigureCanvas(figure)
        toolbar = NavigationToolbar(self.canvas, self)
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(self.canvas)
        plot_widget.setLayout(layout)
        return plot_widget

    def create_plot_window(self):
        if not self.plot_window:
            self.plot_window = QtWidgets.QMdiSubWindow()
            self.plot_window.setWindowIcon(QtGui.QIcon("icons/spike.png"))
        subplot_num = 1 if self.channel_widget.is_avg else len(self.channel_widget.marked_spike_channels)
        self.plot_widget = self.create_plot_widget(subplot_num)
        self.plot_window.setWidget(self.plot_widget)
        self.plot_window.setWindowTitle("Waveform")

    def _set_waveform_default_params(self):
        params = get_default_params()
        for key, value in params["Waveform"].items():
            att = getattr(self, str(key), None)
            if att is not None:
                att.setText(value)
