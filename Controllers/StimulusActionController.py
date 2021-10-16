import numpy as np
import pandas as pd
from Controllers.Controller import Controller
from Controllers.utils import catch_exception
from Modules.stimulus import Stimulus
from Modules.utils import plot_bins, plot_stimulus
from Widgets.StimulusActionWidget import StimulusActionWidget
from Modules.StimulusAction import StimulusAction


class StimulusActionController(Controller):
    def __init__(self, *args):
        self.view = StimulusActionWidget("Description\n On the given tab we are observing the distribution of spikes "
                                         "around stimulus. choose time range so that there is the same type of "
                                         "stimulus. you can analyze several channels or an average of them by "
                                         "selecting average check box. choose stimulus channel with double ")
        super().__init__(*args, self.view)

        self.view.tabs.currentChanged.connect(self._enable_stimulus_if_checked)
        self.view.set_plot_func(self.plot_clicked)
        self.view.set_extract_func(self.extract_clicked)

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

        self.view.create_plot_window("Stimulus Action", "icons/stimulus_action.png")
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
        if len(stimulus_indexes):
            _stimulusAction_obj = self._create_stimulus_action(ch, stimulus_indexes)
            bin_list, bin_list_x, bin_list_stde = self.get_bin_df(_stimulusAction_obj)
            plot_bins(bin_list, bin_list_x, _stimulusAction_obj.bin_width, self.view.canvas, ch, "Bin Timestamp (s)",
                    "Bin Freq (hz)", ax_idx=i, yerr=bin_list_stde)
        plot_stimulus([0], self.view.canvas, ax_idx=i)
    
    def get_bin_df(self, _stimulusAction_obj):
        pre_bin_list, post_bin_list, pre_bin_list_stde, post_bin_list_stde = _stimulusAction_obj.stimulus_bins

        pre_bins_x = np.arange(-len(pre_bin_list), 0) * _stimulusAction_obj.bin_width
        post_bins_x = np.arange(0, len(post_bin_list)) * _stimulusAction_obj.bin_width
        bin_list = np.concatenate((pre_bin_list, post_bin_list))
        bin_list_x = np.concatenate((pre_bins_x, post_bins_x))
        bin_list_stde = np.concatenate((pre_bin_list_stde, post_bin_list_stde))
        return bin_list, bin_list_x, bin_list_stde

    @catch_exception
    def extract_clicked(self):
        path = self.view.get_path_for_save()
        if path:
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

            if self.view.channel_widget.is_avg:
                _stimulusAction_obj = self._create_stimulus_action(marked_channels, stimulus_indexes)              
                bin_list, bin_list_x, bin_list_stde = self.get_bin_df(_stimulusAction_obj)
                stimulus_action_df = pd.DataFrame()
                stimulus_action_df["range"] = bin_list_x
                stimulus_action_df["bin_freq f{marked_channels}"] = bin_list
                stimulus_action_df["bin_freq_std f{marked_channels}"] = bin_list_stde
                stimulus_action_df.to_csv(path + "_stimulus_action.csv", index=False)

            else:
                stimulus_action_df = pd.DataFrame()
                for i, ch in enumerate(marked_channels):
                    _stimulusAction_obj = self._create_stimulus_action(marked_channels, stimulus_indexes)
                    bin_list, bin_list_x, bin_list_stde = self.get_bin_df(_stimulusAction_obj)
                    if i == 0:
                        stimulus_action_df["range"] = bin_list_x
                    stimulus_action_df["bin_freq {ch}"] = bin_list
                    stimulus_action_df["bin_freq_std {ch}"] = bin_list_stde              
                stimulus_action_df.to_csv(path + "_stimulus_action.csv", index=False)

            self.popup_handler.info_popup("Success", "Data Created successfully")

    def _create_stimulus(self, channels):
        useless_stimulus_ranges = list(map(lambda x: x.split("-"), self.view.useless_stimulus_ranges.text().split(",")))
        useless_stimulus_ranges = "" if not useless_stimulus_ranges[0][0] else useless_stimulus_ranges
        return Stimulus(self.view.stimulus_dead_time.text(), self.view.stimulus_threshold_from.text(),
                        self.view.stimulus_threshold_to.text(),useless_stimulus_ranges, self.file.recordings[0].analog_streams[0], channels,
                        self.view.from_s.text(), self.view.to_s.text(), self.view.high_pass.text(), self.view.low_pass.text())
    
    def _create_stimulus_action(self, channels, stimulus_indexes):
        return StimulusAction(self.view.pre.text(), self.view.post.text(), self.view.bin_width.text(), stimulus_indexes,
                              self.view.spike_dead_time.text(), self.view.spike_threshold_from.text(),
                              self.view.spike_threshold_to.text(), self.file.recordings[0].analog_streams[0], channels,
                              self.view.from_s.text(), self.view.to_s.text(), self.view.high_pass.text(), self.view.low_pass.text())
