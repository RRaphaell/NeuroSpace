import numpy as np
import pandas as pd
from Modules.utils import plot_bins
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
        self.view.set_plot_func(self.plot_clicked)
        self.view.set_extract_func(self.extract_clicked)

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
                self.plt_bin_in_channel(marked_channels, 0)
            else:
                for i, ch in enumerate(marked_channels):
                    self.plt_bin_in_channel([ch], i)
            self.view.canvas.figure.tight_layout()

    def plt_bin_in_channel(self, ch, i):
        _bin = self._create_bin(ch)
        bin_range = np.arange(_bin.from_s, _bin.to_s, _bin.bin_width)
        pad_len = len(bin_range) - len(_bin.bins)
        bins = np.concatenate([_bin.bins, [0] * pad_len])
        plot_bins(bins, bin_range, _bin.bin_width, self.view.canvas, ch, "Bin Timestamp (s)", "Bin Freq (hz)", ax_idx=i)


    def extract_clicked(self):
        path = self.view.get_path_for_save()
        if path:
            marked_channels = self.view.channel_widget.marked_spike_channels
            if len(marked_channels) == 0:
                raise ValueError("At least one channel should be marked")

            if self.view.channel_widget.is_avg:
                bin_dataframe = pd.DataFrame()
                bin = self._create_bin(marked_channels)
                bin_range = np.arange(bin.from_s, bin.to_s, bin.bin_width)
                pad_len = len(bin_range) - len(bin.bins)
                bins = np.concatenate([bin.bins, [0]*pad_len])

                bin_dataframe["range"] = bin_range
                bin_dataframe[f"Spikes_frequency_in_bins {marked_channels}"] = bins
                bin_dataframe.to_csv(path + "bins.csv", index=False)

            else:
                bin_dataframe = pd.DataFrame()
                for i, ch in enumerate(marked_channels):
                    bin = self._create_bin([ch])
                    bin_range = np.arange(bin.from_s, bin.to_s, bin.bin_width)
                    pad_len = len(bin_range) - len(bin.bins)
                    bins = np.concatenate([bin.bins, [0]*pad_len])
                    if i == 0:
                        bin_dataframe["range"] = bin_range
                    bin_dataframe[f"Spikes_frequency_in_bins {ch}"] = bins
                bin_dataframe.to_csv(path + "bins.csv", index=False)

    def _create_bin(self, channels):
        return Bin(self.view.bin_width.text(), self.view.spike_dead_time.text(), self.view.spike_threshold_from.text(),
                   self.view.spike_threshold_to.text(), self.file.recordings[0].analog_streams[0],
                   channels, self.view.from_s.text(), self.view.to_s.text(), self.view.high_pass.text(), self.view.low_pass.text())

    def _remove_me(self):
        del self.open_window_dict[self._key]
        self.parameters_dock.setWidget(get_default_widget())
