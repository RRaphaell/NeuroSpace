from Widgets.BinWidget import BinWidget
from Modules.Bin import Bin
from utils import get_default_widget


class BinController:
    def __init__(self, file, key, open_window_dict, mdi, parameters_dock, dialog):
        self.file = file
        self._key = key
        self.open_window_dict = open_window_dict
        self.parameters_dock = parameters_dock
        self._dialog = dialog
        self.mdi = mdi

        self.view = BinWidget()
        self.view.tabs.currentChanged.connect(self._enable_stimulus_if_checked)
        self.view.set_plot_func = self.plot_clicked

    def _enable_stimulus_if_checked(self):
        if len(self.view.channel_widget.marked_stimulus_channels):
            self.view.stimulus_group_box.setEnabled(True)
        else:
            self.view.stimulus_group_box.setDisabled(True)

    def plot_clicked(self):
        if self._dialog:
            self._dialog.accept()
            self._dialog = None
            self.view.create_plot_window()
            self.mdi.addSubWindow(self.view.plot_window)
            self.view.plot_window.show()
            self.view.plot_widget.mousePressEvent = lambda x: self.parameters_dock.setWidget(self.view)
            self.view.plot_window.closeEvent = lambda x: self._remove_me()
            self.view.canvas.mousePressEvent = lambda x: self.parameters_dock.setWidget(self.view)
            self.plot_clicked()
        else:
            marked_channels = self.view.channel_widget.marked_spike_channels
            if len(marked_channels) == 0:
                raise ValueError("At least one channel should be marked")

            if self.view.channel_widget.is_avg:
                waveform = self._create_waveform(marked_channels)
                filtered_signal = waveform.get_filtered_signal()
                plot_signal(filtered_signal, waveform.signal_time_range, self.view.canvas,
                            "Time (seconds)", "Signal (uV)", ax_idx=0)
            else:
                for i, ch in enumerate(marked_channels):
                    waveform = self._create_waveform([ch])
                    filtered_signal = waveform.get_filtered_signal()
                    plot_signal(filtered_signal, waveform.signal_time_range, self.view.canvas,
                                "Time (seconds)", "Signal (uV)", ax_idx=i)
            self.view.canvas.figure.tight_layout()

    def _create_waveform(self, channels):
        return Bin(self.view.bin_width, self.file.recordings[0].analog_streams[0], channels, self.view.from_s.text(),
                        self.view.to_s.text(), self.view.high_pass.text(), self.view.low_pass.text())

    def _remove_me(self):
        del self.open_window_dict[self._key]
        self.parameters_dock.setWidget(get_default_widget())
