from Modules.Spikes import Spikes


class Bin(Spikes):
    def __init__(self, bin_width, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._plot_func = None
        self.bin_width = float(bin_width)
        
    @property
    def bins(self):
        return self._bins

    @property
    def bin_width(self):
        return self._bin_width

    @bin_width.setter
    def bin_width(self, width):
        self._bin_width = width
        self._bins = self._calculate_bins()

    def _calculate_bins(self):
        spike_len_in_bins = []
        spikes_in_range = self.spikes_time_range
        if not len(spikes_in_range):  # when no spikes appear, we should return 0
            return [0]

        spikes_last_index = len(spikes_in_range)-1
        bin_start_second = self.from_s
        counter = 0
        idx = 0

        while True:
            if idx > spikes_last_index:
                spike_len_in_bins.append(counter)
                break
            if spikes_in_range[idx] < (bin_start_second + self.bin_width):
                counter += 1
                idx += 1
            else:
                spike_len_in_bins.append(counter)
                bin_start_second += self.bin_width
                counter = 0

        spike_len_in_bins = list(map(lambda x: int(x / self.bin_width), spike_len_in_bins))
        return spike_len_in_bins
