import numpy as np
from Modules.ParamChecker import ParamChecker
from Modules.Spikes import Spikes
from Modules.utils import calculate_bins


class StimulusAction(Spikes):
    def __init__(self, pre, post, bin_width, stimulus, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pre = pre
        self.post = post 
        self.bin_width = bin_width
        self.stimulus_indexes = stimulus
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
        bin_list = np.zeros(pre_bin_list_size + post_bin_list_size)
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

            bins_together = np.concatenate((pre_bins, post_bins))
            bin_list += bins_together

        bin_list = [b/stimulus_len for b in bin_list]
        return bin_list
