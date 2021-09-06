import numpy as np
from Modules.Spikes import Spikes


class Bin(Spikes):
    def __init__(self, bin_width, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._plot_func = None

    @property
    def bins(self):
        spike_len_in_bins = []
        for b in self.bin_range:
            spike_len_in_bins.append(len(self.spikes[(self.spikes > b) & (self.spikes < b + self.bin_width)]))

        spike_len_in_bins = list(map(lambda x: int(x / self.bin_width), spike_len_in_bins))
        return spike_len_in_bins

    @property
    def bin_range(self):
        bin_ranges = [self.bin_width * i for i in list(range(int(np.ceil((self._to_idx - self._from_idx + 1) / self.fs / self.bin_width))))]
        bin_ranges = np.array(bin_ranges) + self.from_s
        return bin_ranges
