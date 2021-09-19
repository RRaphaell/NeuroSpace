from utils import get_default_widget
from Modules.utils import plot_signal_with_spikes_and_bursts
from Modules.Spikes import Spikes
from Modules.Bursts import Bursts
from Widgets.SpikeWidget import SpikeWidget


class SpikeController:
    def __init__(self, file, key, open_window_dict, mdi, parameters_dock, dialog):
        self.file = file
        self._key = key
        self.open_window_dict = open_window_dict
        self.parameters_dock = parameters_dock
        self._dialog = dialog
        self.mdi = mdi

        self.view = SpikeWidget()
        self.view.tabs.currentChanged.connect(self._enable_stimulus_if_checked)
        self.view.set_plot_func(self.plot_clicked)
        # self.view.set_extract_func(self.extract_clicked)

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
                spike_obj = self._create_spike_module(marked_channels)
                spikes_indexes = spike_obj.spikes_indexes
                spikes_time_range = spike_obj.spikes_time_range
                burst_starts, burst_ends = None, None
                if self.view.burst_group_box.isChecked():
                    bursts_obj = Bursts(spike_obj, self.view.burst_max_start.text(), self.view.burst_max_end.text(),
                                        self.view.burst_betw.text(), self.view.burst_dur.text(), self.view.burst_numb.text())
                    burst_starts, burst_ends = bursts_obj.bursts
                plot_signal_with_spikes_and_bursts(spike_obj.signal, spike_obj.signal_time_range, self.view.canvas,
                                                   "Time (seconds)", "Signal voltage", spikes_time_range,
                                                   spikes_indexes, 0, burst_starts, burst_ends)
            else:
                for i, ch in enumerate(marked_channels):
                    spike_obj = self._create_spike_module([ch])
                    spikes_indexes = spike_obj.spikes_indexes
                    spikes_time_range = spike_obj.spikes_time_range
                    burst_starts, burst_ends = None, None
                    if self.view.burst_group_box.isChecked():   
                        bursts_obj = Bursts(spike_obj, self.view.burst_max_start.text(), self.view.burst_max_end.text(),
                                            self.view.burst_betw.text(), self.view.burst_dur.text(), self.view.burst_numb.text())
                        burst_starts, burst_ends = bursts_obj.bursts
                    plot_signal_with_spikes_and_bursts(spike_obj.signal, spike_obj.signal_time_range, self.view.canvas,
                                                       "Time (seconds)", "Signal voltage", spikes_time_range,
                                                       spikes_indexes, ax_idx=i, bursts_starts=burst_starts,
                                                       bursts_ends=burst_ends)
            self.view.canvas.figure.tight_layout()

    def _create_spike_module(self, marked_channels):
        return Spikes(self.view.spike_dead_time.text(), self.view.spike_threshold_from.text(), self.view.spike_threshold_to.text(),
                      self.file.recordings[0].analog_streams[0], marked_channels, self.view.from_s.text(),
                      self.view.to_s.text(), self.view.high_pass.text(), self.view.low_pass.text())

    def _remove_me(self):
        del self.open_window_dict[self._key]
        self.parameters_dock.setWidget(get_default_widget())
