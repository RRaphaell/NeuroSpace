import numpy as np
from Modules.ParamChecker import ParamChecker
from Modules.Spikes import Spikes
from Modules.utils import calculate_bins


class StimulusAction(Spikes):
    def __init__(self, pre, post, bin_number, stimulus, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pre = pre
        self.post = post 
        self.bin_number = bin_number
        self.bin_width = pre/bin_number
        self.stimulus_indexes = stimulus

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
    def bin_number(self):
        return self.bin_number

    @bin_number.setter
    def bin_number(self, width):
        self.bin_number = ParamChecker(width, "Bin number").not_empty.number.positive.value
    
    def get_stimulus_bins(self):
        spikes = self.indexes
        stimulus_starts = [y for x,y in enumerate(self.stimulus) if x%2 != 0]
        stimulus_ends = [y for x,y in enumerate(self.stimulus) if x%2 == 0]
        bin_width = self.pre/self.bin_number
        bin_list = np.zeros(len(2*self.bin_number))
        for i in range(0,len(stimulus_starts)):
            start = stimulus_starts[i]
            end = stimulus_ends[i]
            from_ = start - int(self.bin_number*self.fs)
            to_ = end + int(self.bin_number*self.fs)
            pre_spikes = spikes[from_:start]
            pre_bins = calculate_bins(pre_spikes, self.from_s, bin_width)
            post_spikes = spikes[start:to_]
            post_bins = calculate_bins(post_spikes, self.from_s, bin_width)
            bins_together = pre_bins + post_bins
            res_list = []
            for i in range(0, len(bins_together)):
                res_list.append(bin_list[i] + bins_together[i])
            bin_list = res_list
        bin_list = [b/len(stimulus_starts) for b in bin_list]
        return bin_list