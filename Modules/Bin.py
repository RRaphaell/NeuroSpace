from Modules.ParamChecker import ParamChecker
from Modules.Spikes import Spikes
from Modules.utils import calculate_bins


class Bin(Spikes):
    """
    Bin module is to give us the information about spikes quantity in bins
    The idea of this class is that the distribution of spikes is easily observable with that bin method.

    Attributes:
        bin_width (float): the desired length (in seconds) for one bin
        bins (list): the list where every element contains the quantity of spikes

    Args:
        bin_width (str): the desired length (in seconds) for one bin
        component_number (str): the possible quantity of neurons who spike

    Note that *args and **kwargs are defined in the parent class
    """
    def __init__(self, bin_width, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._plot_func = None
        self.bin_width = bin_width

    @property
    def bins(self):
        return self._bins

    @property
    def bin_width(self):
        return self._bin_width

    @bin_width.setter
    def bin_width(self, width: str) -> None:
        self._bin_width = ParamChecker(width, "Bin range").not_empty.number.positive.value
        self._bins = self._calculate_bins()

    def _calculate_bins(self) -> list:
        return calculate_bins(self.time_range, self.from_s, self.bin_width)
