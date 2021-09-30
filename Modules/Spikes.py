from Modules.ParamChecker import ParamChecker
from Modules.utils import (calculate_min_voltage_of_signal,
                           calculate_spikes,
                           calculate_threshold_based_on_signal)
from Modules.Waveform import Waveform


class Spikes(Waveform):

    def __init__(self, dead_time, threshold_from="", threshold_to="", *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.dead_time = dead_time
        self.threshold_from = threshold_from
        self.threshold_to = threshold_to
    
    @property
    def indexes(self):
        return calculate_spikes(self.signal, self.threshold_from, self.threshold_to, self.fs, self.dead_time_idx)

    @property
    def time_range(self):
        indexes = self.indexes
        if len(indexes) > 0:
            time_range = indexes/self.fs + self.from_s
            return time_range
        return indexes

    @property
    def dead_time(self):
        return self._dead_time
    
    @dead_time.setter
    def dead_time(self, dead_time):
        _ = ParamChecker(dead_time, "Spike dead time").not_empty.number.positive

        if not ((float(dead_time) >= 0) and (float(dead_time) < self.signal_time)):
            raise ValueError('"Spikes dead time" should be positive')
        self._dead_time = float(dead_time)
        self._dead_time_idx = int(self.dead_time * self.fs)

    @property
    def threshold_from(self):
        return self._threshold_from
    
    @threshold_from.setter
    def threshold_from(self, threshold_from):
        if threshold_from == "":
            self._threshold_from = calculate_threshold_based_on_signal(self.signal)
        else:
            _ = ParamChecker(threshold_from, "Spike threshold from").number

        self._threshold_from = float(threshold_from)

    @property
    def threshold_to(self):
        return self._threshold_to
    
    @threshold_to.setter
    def threshold_to(self, threshold_to):
        if threshold_to == "":
            self._threshold_to = calculate_min_voltage_of_signal(self.signal)
        else:
            self._threshold_to = float(ParamChecker(threshold_to, "Spike threshold to").number.value)

    @property
    def dead_time_idx(self):
        return self._dead_time_idx
    