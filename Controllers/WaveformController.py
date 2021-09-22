import pandas as pd
from Controllers.utils import catch_exception
from Modules.Waveform import Waveform
from Widgets.WaveformWidget import WaveformWidget
from utils import get_default_widget
from Modules.utils import plot_signal


class WaveformController:
    def __init__(self, file, key, open_window_dict, mdi, parameters_dock, popup_handler, dialog):
        self.file = file
        self._key = key
        self.open_window_dict = open_window_dict
        self.parameters_dock = parameters_dock
        self._dialog = dialog
        self.mdi = mdi
        self.popup_handler = popup_handler

        self.view = WaveformWidget(title="Waveform")
        self.view.set_plot_func(self.plot_clicked)
        self.view.set_extract_func(self.extract_clicked)

    @catch_exception
    def plot_clicked(self):
        marked_channels = self.view.channel_widget.marked_spike_channels
        if len(marked_channels) == 0:
            raise ValueError("At least one channel should be marked")

        if self._dialog:
            self._dialog.accept()
            self._dialog = None

        self.view.create_plot_window()
        self.mdi.addSubWindow(self.view.plot_window)

        if self.view.channel_widget.is_avg:
            waveform = self._create_waveform(marked_channels)
            filtered_signal = waveform.signal
            plot_signal(filtered_signal, waveform.signal_time_range, self.view.canvas,
                        "Time (seconds)", "Signal (uV)", ax_idx=0)
        else:
            for i, ch in enumerate(marked_channels):
                waveform = self._create_waveform([ch])
                filtered_signal = waveform.signal
                plot_signal(filtered_signal, waveform.signal_time_range, self.view.canvas,
                            "Time (seconds)", "Signal (uV)", ax_idx=i)

        self.view.plot_window.show()
        self.view.plot_widget.mousePressEvent = lambda x: self.parameters_dock.setWidget(self.view)
        self.view.plot_window.closeEvent = lambda x: self._remove_me()
        self.view.canvas.mousePressEvent = lambda x: self.parameters_dock.setWidget(self.view)
        self.view.canvas.figure.tight_layout()

    @catch_exception
    def extract_clicked(self):
        path = self.view.get_path_for_save()
        if path:
            marked_channels = self.view.channel_widget.marked_spike_channels
            if len(marked_channels) == 0:
                raise ValueError("At least one channel should be marked")

            if self.view.channel_widget.is_avg:
                waveform_dataframe = pd.DataFrame()
                waveform = self._create_waveform(marked_channels)
                waveform_dataframe["time"] = waveform.signal_time_range
                waveform_dataframe[f"Signal_{marked_channels}"] = waveform.signal
                waveform_dataframe.to_csv(path + ".csv", index=False)

            else:
                waveform_dataframe = pd.DataFrame()
                for i, ch in enumerate(marked_channels):
                    waveform = self._create_waveform([ch])
                    if i == 0:
                        waveform_dataframe["time"] = waveform.signal_time_range
                    waveform_dataframe[f"signal_{ch}"] = waveform.signal
                waveform_dataframe.to_csv(path + ".csv", index=False)

    def _create_waveform(self, channels):
        return Waveform(self.file.recordings[0].analog_streams[0], channels, self.view.from_s.text(),
                        self.view.to_s.text(), self.view.high_pass.text(), self.view.low_pass.text())

    def _remove_me(self):
        del self.open_window_dict[self._key]
        self.parameters_dock.setWidget(get_default_widget())
