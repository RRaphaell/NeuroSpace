from PyQt5 import QtWidgets


def merge_widgets(*args, vertical=False):
    layout = QtWidgets.QVBoxLayout() if vertical else QtWidgets.QHBoxLayout()
    for arg in args:
        layout.addWidget(arg)

    widget = QtWidgets.QWidget()
    widget.setLayout(layout)
    return widget


def line_edit_with_label(label, status, default_value):
    line_edit = QtWidgets.QLineEdit(default_value)
    line_edit.setStatusTip(status)
    label = QtWidgets.QLabel(label)

    return line_edit, label


def move_center(frame_gm):
    screen = QtWidgets.QApplication.desktop().screenNumber(QtWidgets.QApplication.desktop().cursor().pos())
    center_point = QtWidgets.QApplication.desktop().screenGeometry(screen).center()
    frame_gm.moveCenter(center_point)
    return frame_gm
