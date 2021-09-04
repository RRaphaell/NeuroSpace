from PyQt5 import QtWidgets, QtCore
from Widgets.utils import merge_widgets, line_edit_with_label, move_center, create_widget_description
from Widgets.ChannelIdsWidget import ChannelIdsWidget
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from Modules.Waveform import Waveform


class WaveformWidget(QtWidgets.QMainWindow):

    def __init__(self, file, mdi, from_s="", to_s="", high_pass="", low_pass="", dialog=None):
        super().__init__()

        self._waveform = None
        self._from_s = None
        self._to_s = None
        self._high_pass = None
        self._low_pass = None
        self._plot_widg = None
        self._canvas = None
        self._is_dialog = dialog
        self._mdi = mdi
        self._plot_window_clicked_func = None
        self._plot_window_close_func = None
        self._file = file

        self.setWindowTitle("Waveform")
        self.move(move_center(self.frameGeometry()).topLeft())

        layout = QtWidgets.QVBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignHCenter)

        waveform_text = create_widget_description("აღწერა \n აქ შეგიძლიათ აირჩიოთ სხვადასხვა არხი და ააგოთ სიგნალი. ააგოთ როგორც არხების საშუალო ასევე სხვადასხვა არხებიც ცალ-ცალკე")
        self._channel_widget = ChannelIdsWidget()
        time_range_widget = self._create_time_range_widgets(from_s, to_s)
        filter_widget = self._create_filter_widgets(high_pass, low_pass)
        buttons_widget = self._create_plot_extract_buttons()

        layout.addWidget(waveform_text)
        layout.addWidget(self._channel_widget)
        layout.addWidget(time_range_widget)
        layout.addWidget(filter_widget)
        layout.addWidget(buttons_widget)
        layout.setAlignment(QtCore.Qt.AlignRight)

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def _create_time_range_widgets(self, from_s, to_s):
        self._from_s, from_s_label = line_edit_with_label("From", "Choose time range", from_s)
        self._to_s, to_s_label = line_edit_with_label("To", "Choose time range", to_s)
        self._from_s.setMaximumWidth(80)
        self._to_s.setMaximumWidth(80)

        time_range_widget = merge_widgets(from_s_label, self._from_s, to_s_label, self._to_s, vertical=False)
        return time_range_widget

    def _create_filter_widgets(self, high_pass, low_pass):
        self._high_pass, high_pass_label = line_edit_with_label("High pass", "Choose high pass filter", high_pass)
        self._low_pass, low_pass_label = line_edit_with_label("Low pass", "choose low_pass filter", low_pass)
        self._high_pass.setMaximumWidth(80)
        self._low_pass.setMaximumWidth(80)

        filter_widget = merge_widgets(high_pass_label, self._high_pass, low_pass_label, self._low_pass, vertical=False)
        return filter_widget

    def _create_plot_extract_buttons(self):
        self._plot_btn = QtWidgets.QPushButton()
        self._plot_btn.setText("Plot Waveform")
        self._plot_btn.setMinimumHeight(40)
        self._plot_btn.setStyleSheet("border: 1px solid black;border-radius: 10px;")
        self._plot_btn.clicked.connect(self._plot_clicked)

        self._extract = QtWidgets.QPushButton()
        self._extract.setText("Extract")
        self._extract.setMinimumHeight(40)
        self._extract.setStyleSheet("border: 1px solid black;border-radius: 10px;")

        buttons_widget = merge_widgets(self._plot_btn, QtWidgets.QSpacerItem(60, 20, QtWidgets.QSizePolicy.Expanding),
                                       self._extract, vertical=False, stretches=[2, 1, 1])
        return buttons_widget

    def _plot_clicked(self):
        if self._plot_widg:
            self._waveform = Waveform(self._file.recordings[0].analog_streams[0],
                                      self._channel_widget.marked_channels, self._canvas,
                                      self._from_s.text(), self._to_s.text(),
                                      self._high_pass.text(), self._low_pass.text())
            self._waveform.plot_waveform()

        if self._is_dialog:
            self._is_dialog.accept()
            self._is_dialog = None

            plot_window = QtWidgets.QMdiSubWindow()
            self._plot_widg = self._create_plot_window(1)
            self._plot_widg.mousePressEvent = lambda x: self._plot_window_clicked_func()
            plot_window.closeEvent = lambda x: self._plot_window_close_func()
            plot_window.setWidget(self._plot_widg)
            plot_window.setWindowTitle("Waveform")
            self._mdi.addSubWindow(plot_window)
            self._plot_widg.show()
            self._plot_clicked()

    def _create_plot_window(self, subplot_num):
        plot_widget = QtWidgets.QWidget()

        figure, _ = plt.subplots(nrows=int(subplot_num ** 0.5), ncols=int(subplot_num/int(subplot_num ** 0.5)))
        self._canvas = FigureCanvas(figure)
        self._canvas.mousePressEvent = lambda x: self._plot_window_clicked_func()
        toolbar = NavigationToolbar(self._canvas, self)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(self._canvas)
        plot_widget.setLayout(layout)
        return plot_widget

    def set_plot_window_clicked_func(self, func):
        self._plot_window_clicked_func = func

    def set_plot_window_close_func(self, func):
        self._plot_window_close_func = func
