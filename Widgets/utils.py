from PyQt5 import QtWidgets, QtCore


def merge_widgets(*args, vertical=False, stretches=[]):
    layout = QtWidgets.QVBoxLayout() if vertical else QtWidgets.QHBoxLayout()
    if len(stretches) and len(stretches) != len(args):
        raise ValueError("Stretches size must be equal to widget sizes")

    for i, arg in enumerate(args):
        if isinstance(arg, QtWidgets.QWidget):
            if len(stretches):
                size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
                size_policy.setHorizontalStretch(stretches[i])
                arg.setSizePolicy(size_policy)
            layout.addWidget(arg)
        else:
            layout.addItem(arg)

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


def create_widget_description(txt):
    description = QtWidgets.QLabel()
    description.setText(txt)
    description.setStyleSheet("border: 1px solid black; padding :10px")
    description.setWordWrap(True)
    description.setAlignment(QtCore.Qt.AlignCenter)
    return description
