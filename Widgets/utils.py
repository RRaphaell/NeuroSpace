from PyQt5 import QtWidgets, QtCore


def merge_widgets(*args, vertical=False, stretches=[]):
    layout = QtWidgets.QVBoxLayout() if vertical else QtWidgets.QHBoxLayout()
    if len(stretches) and len(stretches) != len(args):
        raise ValueError("Stretches size must be equal to widget sizes")

    for i, arg in enumerate(args):
        if isinstance(arg, QtWidgets.QWidget):
            if len(stretches):
                size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
                size_policy.setHorizontalStretch(stretches[i])
                arg.setSizePolicy(size_policy)
            layout.addWidget(arg)
        else:
            layout.addItem(arg)

    widget = QtWidgets.QWidget()
    widget.setLayout(layout)
    return widget


def create_widget_layout(*widgets, vertical=True):
    layout = QtWidgets.QVBoxLayout() if vertical else QtWidgets.QHBoxLayout()
    layout.setAlignment(QtCore.Qt.AlignHCenter)
    for widget in widgets:
        layout.addWidget(widget, 0, QtCore.Qt.AlignHCenter)

    widget = QtWidgets.QWidget()
    widget.setLayout(layout)
    return widget


def move_center(frame_gm):
    screen = QtWidgets.QApplication.desktop().screenNumber(QtWidgets.QApplication.desktop().cursor().pos())
    center_point = QtWidgets.QApplication.desktop().screenGeometry(screen).center()
    frame_gm.moveCenter(center_point)
    return frame_gm


# method to get the divisors
def get_divisors(n):
    divisors = []
    # Note that this loop runs till square root
    i = 1
    while i <= int(n**0.5):
        if n % i == 0:
            # If divisors are equal, print only one
            if n / i == i:
                divisors.append(i)
            else:
                divisors.append(i)
                divisors.append(int(n/i))
        i = i + 1
    return divisors


def calculate_row_col_adjustment(plot_num):
    # if number is prime
    divisors = get_divisors(plot_num)
    divisors.sort()
    if len(divisors) == 2:
        row_adjustment = int(plot_num**0.5)
        col_adjustment = row_adjustment
        while row_adjustment*col_adjustment < plot_num:
            row_adjustment += 1
        return row_adjustment, col_adjustment

    row_adjustment = divisors[len(divisors)//2]
    col_adjustment = int(plot_num / row_adjustment)
    return row_adjustment, col_adjustment
