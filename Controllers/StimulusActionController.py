
import numpy as np
from Modules.stimulus import Stimulus
from Modules.utils import plot_bins, plot_stimulus
from Widgets.StimulusActionWidget import StimulusActionWidget
from Modules.StimulusAction import StimulusAction


class StimulusActionController:
    def __init__(self, file, key, open_window_dict, mdi, parameters_dock, popup_handler, dialog):
        self.file = file
        self._key = key
        self.open_window_dict = open_window_dict
        self.parameters_dock = parameters_dock
        self._dialog = dialog
        self.mdi = mdi
        self.popup_handler = popup_handler


        self.view = StimulusActionWidget()
        self.view.set_plot_func(self.plot_clicked)

    def plot_clicked(self):

        marked_channels = self.view.channel_widget.marked_spike_channels
        stimulus_marked_channels = self.view.channel_widget.marked_stimulus_channels
        if len(stimulus_marked_channels):
            stimulus = self._create_stimulus(stimulus_marked_channels)
            stimulus_time_range = stimulus.time_range
            stimulus_indexes = stimulus.indexes
        else:
            stimulus_time_range = []
            stimulus_indexes = []

        if len(marked_channels) == 0:
            raise ValueError("At least one channel should be marked")

        if self._dialog:
            self._dialog.accept()
            self._dialog = None

        self.view.create_plot_window()
        self.mdi.addSubWindow(self.view.plot_window)

        if self.view.channel_widget.is_avg:
            self.plt_bin_in_channel(marked_channels, stimulus_indexes, 0)
            plot_stimulus(stimulus_time_range, self.view.canvas, ax_idx=0)
        else:
            for i, ch in enumerate(marked_channels):
                self.plt_bin_in_channel([ch], stimulus_indexes, i)
                plot_stimulus(stimulus_time_range, self.view.canvas, ax_idx=i)

        self.view.plot_window.show()
        self.view.plot_widget.mousePressEvent = lambda x: self.parameters_dock.setWidget(self.view)
        self.view.plot_window.closeEvent = lambda x: self._remove_me()
        self.view.canvas.mousePressEvent = lambda x: self.parameters_dock.setWidget(self.view)
        self.view.canvas.figure.tight_layout()

    def plt_bin_in_channel(self, ch, stimulus_indexes, i):
        _stimulusAction_obj = self._create_stimulus_action(ch, stimulus_indexes)
        bin_range = np.arange(_stimulusAction_obj.from_s, _stimulusAction_obj.to_s, _stimulusAction_obj.bin_width)
        pad_len = len(bin_range) - len(_stimulusAction_obj.bins)
        bins = np.concatenate([_stimulusAction_obj.bins, [0] * pad_len])
        plot_bins(bins, bin_range, _stimulusAction_obj.bin_width, self.view.canvas, ch, "Bin Timestamp (s)", "Bin Freq (hz)", ax_idx=i)

    def _create_stimulus(self, channels):
        return Stimulus(self.view.stimulus_dead_time.text(), self.view.stimulus_threshold_from.text(),
                        self.view.stimulus_threshold_to.text(), self.file.recordings[0].analog_streams[0], channels,
                        self.view.from_s.text(), self.view.to_s.text(), self.view.high_pass.text(), self.view.low_pass.text())
    
    def _create_stimulus_action(self, channels, stimulus_indexes):
        return StimulusAction(self.view.pre.text(), self.view.post.text(),self.view.bin_number.text()
                            ,stimulus_indexes,self.view.spike_dead_time.text(), self.view.spike_threshold_from.text()
                            ,self.view.spike_threshold_to.text(), self.file.recordings[0].analog_streams[0], channels
                            ,self.view.from_s.text(), self.view.to_s.text(), self.view.high_pass.text(), self.view.low_pass.text())