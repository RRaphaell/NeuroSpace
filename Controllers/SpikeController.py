from Controllers.utils import catch_exception
from Modules.SpikeTogether import SpikeTogether
import numpy as np
import pandas as pd
from utils import get_default_widget
from Modules.utils import get_spikes_with_labels, plot_signal_with_spikes
from Modules.Bursts import Bursts
from Widgets.SpikeWidget import SpikeWidget


class SpikeController:
    def __init__(self, file, key, open_window_dict, mdi, parameters_dock, popup_handler, dialog):
        self.file = file
        self._key = key
        self.open_window_dict = open_window_dict
        self.parameters_dock = parameters_dock
        self._dialog = dialog
        self.mdi = mdi
        self.popup_handler = popup_handler

        self.view = SpikeWidget()
        self.view.tabs.currentChanged.connect(self._enable_stimulus_if_checked)
        self.view.set_plot_func(self.plot_clicked)
        self.view.set_extract_func(self.extract_clicked)

    def _enable_stimulus_if_checked(self):
        if len(self.view.channel_widget.marked_stimulus_channels):
            self.view.stimulus_group_box.setEnabled(True)
        else:
            self.view.stimulus_group_box.setDisabled(True)

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
            self.plot_one_channel(marked_channels, 0)
        else:
            for i, ch in enumerate(marked_channels):
                self.plot_one_channel([ch], i)

        self.view.plot_window.show()
        self.view.plot_widget.mousePressEvent = lambda x: self.parameters_dock.setWidget(self.view)
        self.view.plot_window.closeEvent = lambda x: self._remove_me()
        self.view.canvas.mousePressEvent = lambda x: self.parameters_dock.setWidget(self.view)
        self.view.canvas.figure.tight_layout()

    def plot_one_channel(self, marked_channels, ax_idx):
        spike_together_obj = self._create_spiketogether_module(marked_channels)

        labels = spike_together_obj.labels
        indices_colors_for_bursts = []    
        indices_colors_for_spikes = get_spikes_with_labels(labels, spike_together_obj.spikes_indexes)

        if self.view.burst_group_box.isChecked():
            bursts_obj = Bursts(spike_together_obj, self.view.burst_max_start.text(), self.view.burst_max_end.text(),
                                self.view.burst_between.text(), self.view.burst_duration.text(), self.view.burst_number.text())
            indices_colors_for_bursts = bursts_obj.bursts_colored_indexes
        plot_signal_with_spikes(spike_together_obj.signal, spike_together_obj.signal_time_range, self.view.canvas,
                                marked_channels, "Time (seconds)", "Signal voltage",indices_colors_for_spikes,
                                ax_idx, indices_colors_for_bursts)

    @catch_exception
    def extract_clicked(self):
        path = self.view.get_path_for_save()
        if path:
            marked_channels = self.view.channel_widget.marked_spike_channels
            if len(marked_channels) == 0:
                raise ValueError("At least one channel should be marked")

            if self.view.channel_widget.is_avg:
                self.extract_spike_dataframe(path,marked_channels)

            else:
                for ch in marked_channels:
                    self.extract_spike_dataframe(path, [ch])

    def extract_spike_dataframe(self, path, marked_channels):
        spike_together_obj = self._create_spiketogether_module(marked_channels)
        spikes_df = pd.DataFrame()
        signal = spike_together_obj.signal
        time_in_sec = spike_together_obj.signal_time_range
        spikes = spike_together_obj.spike_labels_indexes
        spikes_df["time"] = time_in_sec
        spikes_df["signal"] = signal

        to_be_spikes = np.zeros(len(spikes_df))
        if len(spikes) > 0:
            i = 1
            for indices, colors in spikes:
                to_be_spikes[indices] = i
                i+= 1
        spikes_df[f"spikes {marked_channels}"] = to_be_spikes
        if self.view.burst_group_box:
            bursts_obj = Bursts(spike_together_obj, self.view.burst_max_start.text(), self.view.burst_max_end.text(),
                                self.view.burst_between.text(), self.view.burst_duration.text(), self.view.burst_number.text())
            to_be_bursts = np.zeros(len(spikes_df))
            indices_colors_for_bursts = bursts_obj.bursts_colored_indexes
            if len(indices_colors_for_bursts):
                i = 1
                for indices in indices_colors_for_bursts:
                    burst_starts_list = indices[0][0]
                    to_be_bursts[burst_starts_list] = i
                    i+= 1
            spikes_df[f"bursts {marked_channels}"] = to_be_bursts
        else:
            spikes_df[f"bursts {marked_channels}"] = np.zeros(len(spikes_df))
        spikes_df.to_csv(path + "_spikes.csv", index=False)

    def _create_spiketogether_module(self, marked_channels):
        return SpikeTogether(self.view.pre.text(), self.view.post.text(), self.view.component_number.text(),
                             self.view.spike_dead_time.text(), self.view.spike_threshold_from.text(), self.view.spike_threshold_to.text(),
                             self.file.recordings[0].analog_streams[0], marked_channels, self.view.from_s.text(),
                             self.view.to_s.text(), self.view.high_pass.text(), self.view.low_pass.text())

    def _remove_me(self):
        del self.open_window_dict[self._key]
        self.parameters_dock.setWidget(get_default_widget())
