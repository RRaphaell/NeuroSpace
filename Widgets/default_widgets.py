from Widgets.utils import merge_widgets
from PyQt5 import QtWidgets, QtCore


def line_edit_with_label(label, status, default_value):
    line_edit = QtWidgets.QLineEdit(default_value)
    line_edit.setStatusTip(status)
    label = QtWidgets.QLabel(label)
    return line_edit, label


def create_widget_description(txt):
    description = QtWidgets.QLabel()
    description.setText(txt)
    description.setStyleSheet("border: 1px solid black; padding :10px")
    description.setWordWrap(True)
    description.setAlignment(QtCore.Qt.AlignCenter)
    return description


def create_time_range_widgets(from_s, to_s):
    from_s, from_s_label = line_edit_with_label("From", "Choose time range", from_s)
    to_s, to_s_label = line_edit_with_label("To", "Choose time range", to_s)
    from_s.setMaximumWidth(80)
    to_s.setMaximumWidth(80)
    time_range_widget = merge_widgets(from_s_label, from_s, to_s_label, to_s, vertical=False)
    return from_s, to_s, time_range_widget


def create_filter_widgets(high_pass, low_pass):
    high_pass, high_pass_label = line_edit_with_label("High pass", "Choose high pass filter", high_pass)
    low_pass, low_pass_label = line_edit_with_label("Low pass", "choose low_pass filter", low_pass)
    high_pass.setMaximumWidth(80)
    low_pass.setMaximumWidth(80)
    filter_widget = merge_widgets(high_pass_label, high_pass, low_pass_label, low_pass, vertical=False)
    return high_pass, low_pass, filter_widget


def create_plot_extract_buttons():
    plot_btn = QtWidgets.QPushButton()
    plot_btn.setText("Plot Waveform")
    plot_btn.setMinimumHeight(40)
    plot_btn.setStyleSheet("border: 1px solid black;border-radius: 10px;")

    extract_btn = QtWidgets.QPushButton()
    extract_btn.setText("Extract")
    extract_btn.setMinimumHeight(40)
    extract_btn.setStyleSheet("border: 1px solid black;border-radius: 10px;")
    buttons_widget = merge_widgets(plot_btn, QtWidgets.QSpacerItem(60, 20, QtWidgets.QSizePolicy.Expanding),
                                   extract_btn, vertical=False, stretches=[2, 1, 1])
    return plot_btn, extract_btn, buttons_widget

