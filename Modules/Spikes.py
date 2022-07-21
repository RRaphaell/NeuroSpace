from Modules.ParamChecker import ParamChecker
from Modules.utils import (calculate_min_voltage_of_signal,
                           calculate_spikes,
                           calculate_threshold_based_on_signal)
from Modules.Waveform import Waveform


class Spikes(Waveform):
    """
    Spikes class calculates corresponding spikes for the signal.
    Spikes are representations of neural activity, so if we want to
    listen to neurons, we should observe the spikes.


    Attributes:
        dead_time (float): after we find spike, during DEAD_TIME, we shouldn't search for next one
        threshold_from (float): the pre-defined max/min(depends on if signal is negative or not) value of signal
                              to detect spike
        threshold_to (float): the pre-defined max/min(depends on if signal is negative or not) value of signal
                            to detect spike
        indexes (list): the indices of calculated spikes
        time_range (list): the corresponding times of calculated spikes
        dead_time_idx (int): corresponding index of dead_time


    Args:
        dead_time (str): after we find spike, during DEAD_TIME, we shouldn't search for next one
        threshold_from (str): the pre-defined max/min(depends on if signal is negative or not) value of signal
                              to detect spike
        threshold_to (str): the pre-defined max/min(depends on if signal is negative or not) value of signal
                            to detect spike

    Note that *args and **kwargs are defined in the parent class
    """

    def __init__(self, dead_time, threshold_from="", threshold_to="", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dead_time = dead_time
        self.threshold_from = threshold_from
        self.threshold_to = threshold_to
    
    @property
    def indexes(self) -> list:
        return calculate_spikes(self.signal, self.threshold_from, self.threshold_to, self.fs, self.dead_time_idx)

    @property
    def time_range(self) -> list:
        indexes = self.indexes
        if len(indexes) > 0:
            time_range = indexes/self.fs + self.from_s
            return time_range
        return indexes

    @property
    def dead_time(self) -> float:
        return self._dead_time
    
    @dead_time.setter
    def dead_time(self, dead_time: str) -> None:
        _ = ParamChecker(dead_time, "Spike dead time").not_empty.number.positive

        if not ((float(dead_time) >= 0) and (float(dead_time) < self.signal_time)):
            raise ValueError('"Spikes dead time" should be positive')
        self._dead_time = float(dead_time)
        self._dead_time_idx = int(self.dead_time * self.fs)

    @property
    def threshold_from(self) -> float:
        return self._threshold_from
    
    @threshold_from.setter
    def threshold_from(self, threshold_from: str) -> float:
        if threshold_from == "":
            self._threshold_from = calculate_threshold_based_on_signal(self.signal)
        else:
            _ = ParamChecker(threshold_from, "Spike threshold from").number
            
            self._threshold_from = float(threshold_from)

    @property
    def threshold_to(self) -> float:
        return self._threshold_to
    
    @threshold_to.setter
    def threshold_to(self, threshold_to: str) -> None:
        if threshold_to == "":
            min_signal_voltage = calculate_min_voltage_of_signal(self.signal)
            if self.threshold_from > 0 :
                self.threshold_to = min_signal_voltage * (-1)
            else:
                self._threshold_to = min_signal_voltage
        else:
            self._threshold_to = float(ParamChecker(threshold_to, "Spike threshold to").number.value)

    @property
    def dead_time_idx(self) -> int:
        return self._dead_time_idx
    