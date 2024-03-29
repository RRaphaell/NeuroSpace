import numpy as np
import pandas as pd
from Controllers.Controller import Controller
from Controllers.utils import catch_exception
from Modules.stimulus import Stimulus
from Modules.utils import plot_bins, plot_stimulus
from Widgets.BinWidget import BinWidget
from Modules.Bin import Bin


class BinController(Controller):
    """
    BinController class is for UI and module relationship while displaying the bin widget
    On the given widget we are observing the distribution of spikes in bin range.

    Note that, Arguments are documented in parent class
    """
    def __init__(self, *args):
        self.view = BinWidget("Description\n On the given tab we are observing the distribution of spikes in bin range."
                              " you can analyze several channels or an average of them by selecting average check box. "
                              "choose stimulus channel with double click on channel id")
        super().__init__(*args, self.view)

        self.view.tabs.currentChanged.connect(self._enable_stimulus_if_checked)
        self.view.set_plot_func(self.plot_clicked)
        self.view.set_extract_func(self.extract_clicked)

    @catch_exception
    def plot_clicked(self) -> None:
        """
        This function firstly makes the bin module object, preprocesses signal and then uses
        bin plot function from utils to plot the calculated bins.
        """
        marked_channels = self.view.channel_widget.marked_spike_channels
        if len(marked_channels) == 0:
            raise ValueError("At least one channel should be marked")

        if self._dialog:
            self._dialog.accept()
            self._dialog = None

        self.view.create_plot_window("Bin", "icons/bin.png")
        self.mdi.addSubWindow(self.view.plot_window)

        stimulus_time_range = self._get_stimulus_time_range()

        if self.view.channel_widget.is_avg:
            self.plt_bin_in_channel(marked_channels, 0)
            plot_stimulus(stimulus_time_range, self.view.canvas, ax_idx=0)
        else:
            for i, ch in enumerate(marked_channels):
                self.plt_bin_in_channel([ch], i)
                plot_stimulus(stimulus_time_range, self.view.canvas, ax_idx=i)

        self.view.plot_window.show()
        self.view.plot_widget.mousePressEvent = lambda x: self.parameters_dock.setWidget(self.view)
        self.view.plot_window.closeEvent = lambda x: self._remove_me()
        self.view.canvas.mousePressEvent = lambda x: self.parameters_dock.setWidget(self.view)
        self.view.canvas.figure.tight_layout()

    def plt_bin_in_channel(self, ch, i) -> None:
        """
        This function firstly makes the waveform module object, preprocesses signal and then uses
        waveform plot function from utils to plot the desired signal.

        Args:
            ch (list -> str): user's chosen channels list
            i (int): ax index to draw
        """
        _bin = self._create_bin(ch)
        bin_range = np.arange(_bin.from_s, _bin.to_s, _bin.bin_width)
        pad_len = len(bin_range) - len(_bin.bins)
        bins = np.concatenate([_bin.bins, [0] * pad_len])
        plot_bins(bins, bin_range, _bin.bin_width, self.view.canvas, ch, "Bin Timestamp (s)", "Bin Freq (hz)", ax_idx=i)

    @catch_exception
    def extract_clicked(self):
        """
        This function firstly makes the bin module object, preprocesses signal, calculates bins
        and then extracts desired signals bins into the user's desired input path
        """
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

            self.popup_handler.info_popup("Success", "Data Created successfully")

    def _get_stimulus_time_range(self) -> list:
        """
        This function creates stimulus object and then returns the current signal's stimulus times as a list

        Returns:
            stimulus time range (list): corresponding stimulus's times
        """
        stimulus_marked_channels = self.view.channel_widget.marked_stimulus_channels
        if len(stimulus_marked_channels):
            stimulus = self._create_stimulus(stimulus_marked_channels)
            return stimulus.time_range
        return []

    def _create_bin(self, channels: list) -> Bin:
        """
        This function creates stimulus object and then returns the current signal's stimulus times as a list

        Returns:
            stimulus time range (list): corresponding stimulus's times
        """
        return Bin(self.view.bin_width.text(), self.view.spike_dead_time.text(), self.view.spike_threshold_from.text(),
                   self.view.spike_threshold_to.text(), self.file.recordings[0].analog_streams[0],
                   channels, self.view.from_s.text(), self.view.to_s.text(), self.view.high_pass.text(), self.view.low_pass.text())

    def _create_stimulus(self, channels: list) -> Stimulus:
        """
        Creates stimulus class object
        """
        return Stimulus(self.view.stimulus_dead_time.text(), self.view.stimulus_threshold_from.text(),
                        self.view.stimulus_threshold_to.text(), "", self.file.recordings[0].analog_streams[0], channels,
                        self.view.from_s.text(), self.view.to_s.text(), self.view.high_pass.text(), self.view.low_pass.text())
