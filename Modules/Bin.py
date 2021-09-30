from Modules.ParamChecker import ParamChecker
from Modules.Spikes import Spikes
from Modules.utils import calculate_bins


class Bin(Spikes):
    def __init__(self, bin_width, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print(bin_width)
        self._plot_func = None
        self.bin_width = bin_width
        
    @property
    def bins(self):
        return self._bins

    @property
    def bin_width(self):
        return self._bin_width

    @bin_width.setter
    def bin_width(self, width):
        self._bin_width = ParamChecker(width, "Bin range").not_empty.number.positive.value
        self._bins = self._calculate_bins()

    def _calculate_bins(self):
        return calculate_bins(self.time_range, self.from_s, self.bin_width)