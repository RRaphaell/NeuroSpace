from PyQt5 import QtWidgets, QtGui
from Widgets.utils import merge_widgets, line_edit_with_label, move_center
import dictionary

CHOSEN_LANG = "EN"

class WaveformWidget(QtWidgets.QMainWindow):
    def __init__(self, from_s="", to_s="", high_pass="", low_pass=""):
        super().__init__()

        self._from_s = None
        self._to_s = None
        self._high_pass = None
        self._low_pass = None
        self.setWindowTitle(dictionary.WAVEFORM[CHOSEN_LANG])
        self.move(move_center(self.frameGeometry()).topLeft())
        self.setFixedSize(800, 400)

        layout = QtWidgets.QGridLayout()

        waveform_text = QtWidgets.QLabel()
        waveform_text.setText(dictionary.WAVEFORM_TAB_TEXT[CHOSEN_LANG])
        temp = QtWidgets.QPushButton()
        temp.setText(dictionary.BUTTON[CHOSEN_LANG])

        time_range_widget = self._create_time_range_widgets(from_s, to_s)
        filter_widget = self._create_filter_widgets(high_pass, low_pass)
        buttons_widget = self._create_plot_extract_buttons()

        layout.addWidget(waveform_text, 0, 0)
        layout.addWidget(temp, 0, 1)
        layout.addWidget(time_range_widget, 1, 0, 1, 2)
        layout.addWidget(filter_widget, 2, 0, 1, 2)
        layout.addWidget(buttons_widget, 3, 0, 1, 2)

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def _create_time_range_widgets(self, from_s, to_s):
        self._from_s, from_s_label = line_edit_with_label(
            dictionary.FROM[CHOSEN_LANG], dictionary.CHOOSE[CHOSEN_LANG] +
            dictionary.TIME_RANGE[CHOSEN_LANG], from_s)
        self._to_s, to_s_label = line_edit_with_label(
            dictionary.TO[CHOSEN_LANG], dictionary.CHOOSE[CHOSEN_LANG] +
            dictionary.TIME_RANGE[CHOSEN_LANG], to_s)

        time_range_widget = merge_widgets(from_s_label,
                                          self._from_s,
                                          to_s_label,
                                          self._to_s,
                                          vertical=False)
        return time_range_widget

    def _create_filter_widgets(self, high_pass, low_pass):
        self._high_pass, high_pass_label = line_edit_with_label(
            dictionary.HIGH_PASS[CHOSEN_LANG], dictionary.CHOOSE[CHOSEN_LANG] +
            dictionary.HIGH_PASS[CHOSEN_LANG] + dictionary.FILTER[CHOSEN_LANG],
            high_pass)
        self._low_pass, low_pass_label = line_edit_with_label(
            dictionary.LOW_PASS[CHOSEN_LANG], dictionary.CHOOSE[CHOSEN_LANG] +
            dictionary.LOW_PASS[CHOSEN_LANG] + dictionary.FILTER[CHOSEN_LANG],
            low_pass)

        filter_widget = merge_widgets(high_pass_label,
                                      self._high_pass,
                                      low_pass_label,
                                      self._low_pass,
                                      vertical=False)
        return filter_widget

    def _create_plot_extract_buttons(self):
        self._plot = QtWidgets.QPushButton()
        self._plot.setText(dictionary.PLOT[CHOSEN_LANG] +
                           dictionary.WAVEFORM[CHOSEN_LANG])

        self._extract = QtWidgets.QPushButton()
        self._extract.setText(dictionary.EXTRACT[CHOSEN_LANG])

        buttons_widget = merge_widgets(self._plot,
                                       self._extract,
                                       vertical=False)
        return buttons_widget
