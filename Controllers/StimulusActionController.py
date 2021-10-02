import numpy as np
from Controllers.Controller import Controller
from Controllers.utils import catch_exception
from Modules.stimulus import Stimulus
from Modules.utils import plot_bins
from Widgets.StimulusActionWidget import StimulusActionWidget
from Modules.StimulusAction import StimulusAction


class StimulusActionController(Controller):
    def __init__(self, *args):
        self.view = StimulusActionWidget()
        super().__init__(*args, self.view)

        self.view.tabs.currentChanged.connect(self._enable_stimulus_if_checked)
        self.view.set_plot_func(self.plot_clicked)

    @catch_exception
    def plot_clicked(self):

        marked_channels = self.view.channel_widget.marked_spike_channels
        stimulus_marked_channels = self.view.channel_widget.marked_stimulus_channels
        if len(stimulus_marked_channels):
            stimulus = self._create_stimulus(stimulus_marked_channels)
            stimulus_indexes = stimulus.indexes
        else:
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
        else:
            for i, ch in enumerate(marked_channels):
                self.plt_bin_in_channel([ch], stimulus_indexes, i)

        self.view.plot_window.show()
        self.view.plot_widget.mousePressEvent = lambda x: self.parameters_dock.setWidget(self.view)
        self.view.plot_window.closeEvent = lambda x: self._remove_me()
        self.view.canvas.mousePressEvent = lambda x: self.parameters_dock.setWidget(self.view)
        self.view.canvas.figure.tight_layout()

    def plt_bin_in_channel(self, ch, stimulus_indexes, i):
        _stimulusAction_obj = self._create_stimulus_action(ch, stimulus_indexes)
        bins = _stimulusAction_obj.stimulus_bins
        bin_range = np.arange(0-_stimulusAction_obj.pre, _stimulusAction_obj.post, _stimulusAction_obj.bin_width)
        plot_bins(bins, bin_range, _stimulusAction_obj.bin_width, self.view.canvas, ch, "Bin Timestamp (s)", "Bin Freq (hz)", ax_idx=i)

    def _create_stimulus(self, channels):
        return Stimulus(self.view.stimulus_dead_time.text(), self.view.stimulus_threshold_from.text(),
                        self.view.stimulus_threshold_to.text(), self.file.recordings[0].analog_streams[0], channels,
                        self.view.from_s.text(), self.view.to_s.text(), self.view.high_pass.text(), self.view.low_pass.text())
    
    def _create_stimulus_action(self, channels, stimulus_indexes):
        return StimulusAction(self.view.pre.text(), self.view.post.text(),self.view.bin_width.text(),
                              stimulus_indexes, self.view.spike_dead_time.text(), self.view.spike_threshold_from.text(),
                              self.view.spike_threshold_to.text(), self.file.recordings[0].analog_streams[0], channels,
                              self.view.from_s.text(), self.view.to_s.text(), self.view.high_pass.text(), self.view.low_pass.text())