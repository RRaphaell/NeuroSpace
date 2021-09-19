from Widgets.utils import merge_widgets
from PyQt5 import QtWidgets, QtCore


def line_edit_with_label(label, status, default_value):
    line_edit = QtWidgets.QLineEdit(default_value)
    line_edit.setStatusTip(status)
    line_edit.setMaximumWidth(70)
    label = QtWidgets.QLabel(label)
    return line_edit, label


def create_pair_line_edit(label1, label2, status1, status2, default1="", default2=""):
    line_edit1, line_label1 = line_edit_with_label(label1, status1, default1)
    line_edit2, line_label2 = line_edit_with_label(label2, status2, default2)
    widget = merge_widgets(line_label1, line_edit1, line_label2, line_edit2, vertical=False)
    return line_edit1, line_edit2, widget


def create_time_range_widgets(from_s="", to_s=""):
    _from_s, _to_s, time_range_widget = create_pair_line_edit("From", "To",
                                                              "Choose time range", "Choose time range",
                                                              default1=from_s, default2=to_s)
    return _from_s, _to_s, time_range_widget


def create_filter_widgets(high_pass="", low_pass=""):
    _high_pass, _low_pass, filter_widget = create_pair_line_edit("High pass", "Low pass",
                                                                 "Choose filter range", "Choose filter range",
                                                                 default1=high_pass, default2=low_pass)
    return _high_pass, _low_pass, filter_widget


def create_threshold_widgets(threshold_from="", threshold_to=""):
    _threshold_from, _threshold_to, threshold_widget = create_pair_line_edit("Threshold From", "To",
                                                                             "Choose threshold range",
                                                                             "Choose threshold range",
                                                                             default1=threshold_from,
                                                                             default2=threshold_to)
    return _threshold_from, _threshold_to, threshold_widget


def create_widget_description(txt):
    description = QtWidgets.QLabel()
    description.setText(txt)
    description.setStyleSheet("border: 1px solid black; padding :10px")
    description.setWordWrap(True)
    description.setAlignment(QtCore.Qt.AlignCenter)
    return description


def create_plot_extract_buttons():
    plot_btn = QtWidgets.QPushButton()
    plot_btn.setText("Plot")
    plot_btn.setMinimumSize(60, 40)
    plot_btn.setStyleSheet("border: 1px solid black;border-radius: 10px;")

    extract_btn = QtWidgets.QPushButton()
    extract_btn.setText("Extract")
    extract_btn.setMinimumSize(60, 40)
    extract_btn.setStyleSheet("border: 1px solid black;border-radius: 10px;")
    buttons_widget = merge_widgets(plot_btn, QtWidgets.QSpacerItem(60, 20, QtWidgets.QSizePolicy.Expanding),
                                   extract_btn, vertical=False, stretches=[2, 1, 1])
    return plot_btn, extract_btn, buttons_widget


def create_group_dead_time_threshold(title):
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
