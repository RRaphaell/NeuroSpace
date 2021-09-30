from PyQt5 import QtWidgets
from functools import partial
from Widgets.utils import merge_widgets

RED = "background-color : rgb(255,51,51)"
GREEN = "background-color : rgb(51,255,51)"
GRAY = "background-color : light grey"


class ChannelIdsWidget(QtWidgets.QGroupBox):
    def __init__(self, stimulus_option=False):
        super().__init__("Channel id")

        layout = QtWidgets.QVBoxLayout()
        self._check_all_butt = None
        self._average_butt = None
        self._buttons = {}
        self.button_positions = [GRAY, GREEN, RED] if stimulus_option else [GRAY, GREEN]
        self._is_stimulus_selected = False

        channel_widget = QtWidgets.QWidget()
        self._channel_layout = QtWidgets.QGridLayout()
        channel_widget.setLayout(self._channel_layout)
        self._create_channel_ids()
        button_widget = self._create_checkable_buttons()

        layout.addWidget(channel_widget)
        layout.addWidget(button_widget)
        self.setLayout(layout)
        self.setFixedSize(300, 400)

    def _create_checkable_buttons(self):
        self._check_all_butt = QtWidgets.QCheckBox("Clear")
        self._check_all_butt.clicked.connect(self._check_all)
        self._average_butt = QtWidgets.QCheckBox("Average")

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
                    button.setFixedSize(30, 30)
                    button.clicked.connect(partial(self._change_color, button))
                    self._channel_layout.addWidget(button, row - 1, col - 1)
                    self._buttons[button] = 0

    def _check_all(self, on):
        for button in self._buttons.keys():
            self._buttons[button] = on
            button.setStyleSheet(self.button_positions[on])
        self._is_stimulus_selected = False

    @ property
    def is_avg(self):
        return self._average_butt.isChecked()

    @property
    def marked_spike_channels(self):
        return self._get_channel_based_on_color(GREEN)

    @property
    def marked_stimulus_channels(self):
        return self._get_channel_based_on_color(RED)

    def _get_channel_based_on_color(self, color):
        marked_buttons = []
        for button, position in self._buttons.items():
            if self.button_positions[position] == color:
                marked_buttons.append(button.text())
        return marked_buttons

    def _change_color(self, button_key):
        position = self._buttons[button_key]
        # when stimulus channel is unchecked
        if self.button_positions[position] == RED:
            self._is_stimulus_selected = False

        position = (position + 1) % len(self.button_positions)
        if self.button_positions[position] == RED:
            if self._is_stimulus_selected:
                position = (position + 1) % len(self.button_positions)
            else:
                self._is_stimulus_selected = True

        button_key.setStyleSheet(self.button_positions[position])
        self._buttons[button_key] = position

    @staticmethod
    def is_square(num):
        square_root = num ** 0.5
        module = square_root % 1
        return module == 0
