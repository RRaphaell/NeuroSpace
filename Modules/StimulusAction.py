import numpy as np
from Modules.ParamChecker import ParamChecker
from Modules.Spikes import Spikes
from Modules.utils import calculate_bins
from functools import reduce


class StimulusAction(Spikes):
    def __init__(self, pre, post, bin_width, stimulus, useless_stimulus_ranges, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pre = pre
        self.post = post 
        self.bin_width = bin_width
        self.stimulus_indexes = stimulus
        self._useless_stimulus_ranges = useless_stimulus_ranges
        self.stimulus_bins = self.get_stimulus_bins()

    @property
    def pre(self):
        return self._pre

    @pre.setter
    def pre(self, value):
        self._pre = ParamChecker(value, "Pre").not_empty.number.positive.value

    @property
    def post(self):
        return self._post

    @post.setter
    def post(self, value):
        self._post = ParamChecker(value, "Post").not_empty.number.positive.value

    @property
    def bin_width(self):
        return self._bin_width

    @bin_width.setter
    def bin_width(self, width):
        self._bin_width = ParamChecker(width, "Bin width").not_empty.number.positive.value
    
    def get_stimulus_bins(self):
        spikes = self.indexes  # This spikes are just indexes, from_in_s IS NOT added here
        # here are stimulus indexes which also DOES NOT include from_in_s here
        stimulus_starts = [y for x, y in enumerate(self.stimulus_indexes) if x % 2 != 0]
        stimulus_ends = [y for x, y in enumerate(self.stimulus_indexes) if x % 2 == 0]

        # in case stimulus lists have no equal size
        stimulus_len = len(stimulus_starts) if len(stimulus_starts) <= len(stimulus_ends) else len(stimulus_ends)
        pre_bin_list_size = int(self.pre/self.bin_width)
        post_bin_list_size = int(self.post/self.bin_width)
        pre_bin_list, post_bin_list = [], []
        for i in range(0, stimulus_len):
            start = stimulus_starts[i]  # index
            end = stimulus_ends[i]  # index
            from_ = start - int(self.pre * self.fs)
            to_ = end + int(self.post * self.fs)

            pre_spikes = spikes[(spikes > from_) & (spikes < start)]
            pre_spikes = [sp/self.fs + self.from_s for sp in pre_spikes]
            pre_bins = calculate_bins(pre_spikes, start/self.fs-self.pre+self.from_s, self.bin_width)
            pad_len = pre_bin_list_size - len(pre_bins)
            pre_bins = np.concatenate((pre_bins, [0] * pad_len))

            post_spikes = spikes[(spikes > end) & (spikes < to_)]
            post_spikes = [sp/self.fs + self.from_s for sp in post_spikes]
            post_bins = calculate_bins(post_spikes, end/self.fs+self.from_s, self.bin_width)
            pad_len = post_bin_list_size - len(post_bins)
            post_bins = np.concatenate((post_bins, [0] * pad_len))

            pre_bin_list.append(list(pre_bins))
            post_bin_list.append(list(post_bins))

        pre_bin_list, post_bin_list = np.array(pre_bin_list), np.array(post_bin_list)
        pre_bin_list_sum, pre_bin_list_std = np.sum(pre_bin_list, axis=0), np.std(pre_bin_list, axis=0)

        pre_bin_list_stde = pre_bin_list_std / np.sqrt(pre_bin_list.shape[0])

        post_bin_list_sum, post_bin_list_std = np.sum(post_bin_list, axis=0), np.std(post_bin_list, axis=0)
        post_bin_list_stde = post_bin_list_std / np.sqrt(post_bin_list.shape[0])

        pre_bin_list = pre_bin_list_sum / stimulus_len
        post_bin_list = post_bin_list_sum / stimulus_len
        return pre_bin_list, post_bin_list, pre_bin_list_stde, post_bin_list_stde
