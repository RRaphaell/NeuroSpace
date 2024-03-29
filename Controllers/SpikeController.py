from Controllers.Controller import Controller
from Modules.stimulus import Stimulus
from Controllers.utils import catch_exception
from Modules.SpikeTogether import SpikeTogether
import numpy as np
import pandas as pd
from Modules.utils import get_spikes_with_labels, plot_signal_with_spikes, plot_stimulus
from Modules.Bursts import Bursts
from Widgets.SpikeWidget import SpikeWidget


class SpikeController(Controller):
    """
    BinController class is for UI and module relationship while displaying the spike controller widget
    On the given tab we are observing activity of the signal referring to
    spikes bursts and stimulus, for unit or multi-neural activities

    Note that, Arguments are documented in parent class
    """
    def __init__(self, *args):
        self.view = SpikeWidget("Description\n On the given tab we are observing activity of the signal referring to "
                                "spikes bursts and stimulus, for unit or multi-neural activities "
                                "you can analyze several channels or an average of them by "
                                "selecting average check box. choose stimulus channel with double click on channel id")
        super().__init__(*args, self.view)

        self.view.tabs.currentChanged.connect(self._enable_stimulus_if_checked)
        self.view.set_plot_func(self.plot_clicked)
        self.view.set_extract_func(self.extract_clicked)


    @catch_exception
    def plot_clicked(self):
        """
        This function firstly makes the spike module object, preprocesses signal and then uses
        plot_one_channel function to plot the calculated spikes.
        """
        marked_channels = self.view.channel_widget.marked_spike_channels
        if len(marked_channels) == 0:
            raise ValueError("At least one channel should be marked")

        if self._dialog:
            self._dialog.accept()
            self._dialog = None

        self.view.create_plot_window("Spike", "icons/spike.png")
        self.mdi.addSubWindow(self.view.plot_window)
        stimulus_marked_channels = self.view.channel_widget.marked_stimulus_channels
        if self.view.channel_widget.is_avg:
            self.plot_one_channel(marked_channels, stimulus_marked_channels, 0)
        else:
            for i, ch in enumerate(marked_channels):
                self.plot_one_channel([ch], stimulus_marked_channels, i)

        self.view.plot_window.show()
        self.view.plot_widget.mousePressEvent = lambda x: self.parameters_dock.setWidget(self.view)
        self.view.plot_window.closeEvent = lambda x: self._remove_me()
        self.view.canvas.mousePressEvent = lambda x: self.parameters_dock.setWidget(self.view)
        self.view.canvas.figure.tight_layout()

    def plot_one_channel(self, marked_channels: list, stimulus_marked_channels: list, ax_idx: int):
        """
        This function plots one particular channels spikes and stimulus if the length of the
        marked_channels is 1, if not, then it averages the signal and plots the above mentioned things so.

        Args:
            marked_channels (list): user's chosen channels list
            stimulus_marked_channels (list): user's chosen stimulus channels list
            ax_idx (int): the index to plot
        """
        spike_together_obj = self._create_spiketogether_module(marked_channels)

        labels = spike_together_obj.labels
        indices_colors_for_bursts = []    
        indices_colors_for_spikes = get_spikes_with_labels(labels, spike_together_obj.indexes)
        if len(stimulus_marked_channels):
            stimulus = self._create_stimulus(stimulus_marked_channels)
            stimulus_time_range = stimulus.time_range
        else:
            stimulus_time_range = []
        if self.view.burst_group_box.isChecked():
            bursts_obj = Bursts(spike_together_obj, self.view.burst_max_start.text(), self.view.burst_max_end.text(),
                                self.view.burst_between.text(), self.view.burst_duration.text(), self.view.burst_number.text())
            indices_colors_for_bursts = bursts_obj.bursts_colored_indexes

        plot_signal_with_spikes(spike_together_obj.signal, spike_together_obj.time, spike_together_obj.fs, self.view.canvas,
                                marked_channels, "Time (seconds)", "Signal voltage", indices_colors_for_spikes,
                                ax_idx, indices_colors_for_bursts)
        plot_stimulus(stimulus_time_range, self.view.canvas, ax_idx=ax_idx)


    @catch_exception
    def extract_clicked(self):
        """
        This function helps us extract spikes into the desired dataframe
        """
        path = self.view.get_path_for_save()
        if path:
            marked_channels = self.view.channel_widget.marked_spike_channels
            if len(marked_channels) == 0:
                raise ValueError("At least one channel should be marked")   
            stimulus_marked_channels = self.view.channel_widget.marked_stimulus_channels
            if self.view.channel_widget.is_avg:
                self.extract_spike_dataframe(path, marked_channels, stimulus_marked_channels)

            else:
                for ch in marked_channels:
                    self.extract_spike_dataframe(path, [ch], stimulus_marked_channels)

            self.popup_handler.info_popup("Success", "Data Created successfully")

    def extract_spike_dataframe(self, path: str, marked_channels: list, stimulus_marked_channels: list) -> None:
        """
        This function firstly makes the spike module object, preprocesses signal, calculates spikes
        with appropriate parameters and then extracts those spikes into the user's desired input path

        Args:
            path (str): path to save the dataframe
            marked_channels (list): marked spike channels
            stimulus_marked_channels (list): marked stimulus channels
        """
        spike_together_obj = self._create_spiketogether_module(marked_channels)
        spikes_df = pd.DataFrame()
        signal = spike_together_obj.signal
        time_in_sec = spike_together_obj.time
        spikes = spike_together_obj.spike_labels_indexes
        spikes_df["time"] = time_in_sec
        spikes_df["signal"] = signal

        to_be_spikes = np.zeros(len(spikes_df))
        if len(spikes) > 0:
            i = 1
            for indices, colors in spikes:
                to_be_spikes[indices] = i
                i += 1
        spikes_df[f"spikes {marked_channels}"] = to_be_spikes
        if self.view.burst_group_box.isChecked():
            bursts_obj = Bursts(spike_together_obj, self.view.burst_max_start.text(), self.view.burst_max_end.text(),
                                self.view.burst_between.text(), self.view.burst_duration.text(), self.view.burst_number.text())
            to_be_bursts = np.zeros(len(spikes_df))
            indices_colors_for_bursts = bursts_obj.bursts_colored_indexes
            if len(indices_colors_for_bursts):
                i = 1
                for indices in indices_colors_for_bursts:
                    burst_starts_list = indices[0][0]
                    to_be_bursts[burst_starts_list] = i
                    i += 1
            spikes_df[f"bursts {marked_channels}"] = to_be_bursts
        else:
            spikes_df[f"bursts {marked_channels}"] = np.zeros(len(spikes_df))
        if len(stimulus_marked_channels):
            stimulus = self._create_stimulus(stimulus_marked_channels)
            stimulus_indexes = stimulus.indexes
            to_be_stimulus = np.zeros(len(spikes_df))
            if len(stimulus_indexes):
                to_be_stimulus[stimulus_indexes] = 1
            spikes_df["Stimulus"] = to_be_stimulus
        spikes_df.to_csv(path +f" {marked_channels} "+"_spikes.csv", index=False)

    def _create_spiketogether_module(self, marked_channels: list) -> SpikeTogether:
        """
        Creates spiketogether class object
        """
        return SpikeTogether(self.view.pre.text(), self.view.post.text(), self.view.component_number.text(),
                             self.view.spike_dead_time.text(), self.view.spike_threshold_from.text(), self.view.spike_threshold_to.text(),
                             self.file.recordings[0].analog_streams[0], marked_channels, self.view.from_s.text(),
                             self.view.to_s.text(), self.view.high_pass.text(), self.view.low_pass.text())

    def _create_stimulus(self, channels: list) -> Stimulus:
        """
        Creates stimulus class object
        """
        return Stimulus(self.view.stimulus_dead_time.text(), self.view.stimulus_threshold_from.text(),
                        self.view.stimulus_threshold_to.text(), self.file.recordings[0].analog_streams[0], channels,
                        self.view.from_s.text(), self.view.to_s.text(), self.view.high_pass.text(), self.view.low_pass.text())
