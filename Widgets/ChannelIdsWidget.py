from PyQt5 import QtWidgets
from functools import partial
from Widgets.utils import merge_widgets


class ChannelIdsWidget(QtWidgets.QGroupBox):
    def __init__(self):
        super().__init__("Channel id")

        layout = QtWidgets.QVBoxLayout()
        self._check_all_butt = None
        self._average_butt = None
        self._buttons = []

        channel_widget = QtWidgets.QWidget()
        self._channel_layout = QtWidgets.QGridLayout()
        channel_widget.setLayout(self._channel_layout)
        self._create_channel_ids()
        button_widget = self._create_checkable_buttons()

        layout.addWidget(channel_widget)
        layout.addWidget(button_widget)
        self.setLayout(layout)
        # self.setFixedWidth(300)

    def _create_checkable_buttons(self):
        self._check_all_butt = QtWidgets.QCheckBox("Clear")
        self._check_all_butt.clicked.connect(self._check_all)
        self._average_butt = QtWidgets.QCheckBox("Use Average")

        buttons_widget = merge_widgets(self._check_all_butt, QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding),
                                       self._average_butt,  vertical=False)
        return buttons_widget

    def _create_channel_ids(self, channel_num=64):
        if not ChannelIdsWidget.is_square(channel_num):
            raise ValueError("Channel quantity should be square")

        root = int(channel_num**0.5)
        corner_buttons = [(1, 1), (1, root), (root, 1), (root, root)]
        for row in range(1, root+1):
            for col in range(1, root + 1):
                if (col, row) not in corner_buttons:
                    button = QtWidgets.QPushButton(f"{col}{row}")
                    button.setCheckable(True)
                    button.setFixedSize(30, 30)
                    button.clicked.connect(partial(ChannelIdsWidget._change_color, button))
                    self._channel_layout.addWidget(button, row - 1, col - 1)
                    self._buttons.append(button)

    def _check_all(self, on):
        for button in self._buttons:
            if on:
                button.setStyleSheet("background-color : rgb(102,255,102)")
            else:
                button.setStyleSheet("background-color : light grey")
            button.setChecked(on)

    @ property
    def is_avg(self):
        return self._average_butt.isChecked()

    @property
    def marked_channels(self):
        marked_buttons = []
        for button in self._buttons:
            if button.isChecked():
                marked_buttons.append(button.text())
        return marked_buttons

    @staticmethod
    def _change_color(button):
        if button.isChecked():
            button.setStyleSheet("background-color : rgb(102,255,102)")
        else:
            button.setStyleSheet("background-color : light grey")

    @staticmethod
    def is_square(num):
        square_root = num ** 0.5
        module = square_root % 1
        return module == 0
