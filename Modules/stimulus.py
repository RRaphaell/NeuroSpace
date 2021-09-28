from Modules.ParamChecker import ParamChecker
from Modules.Waveform import Waveform
from Modules.utils import calculate_min_voltage_of_signal, calculate_stimulus


class Stimulus(Waveform):
    def __init__(self,  dead_time, threshold_from, threshold_to, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dead_time = dead_time
        self.threshold_from = threshold_from
        self.threshold_to = threshold_to

    @property
    def indexes(self):
        return calculate_stimulus(self.signal, self.threshold_from, self.dead_time_idx)

    @property
    def time_range(self):
        indexes = self.indexes
        if len(indexes) > 1:
            time_range = indexes/self.fs + self.from_s
            return time_range
        return indexes

    @property
    def dead_time(self):
        return self._dead_time

    @property
    def dead_time_idx(self):
        return self._dead_time_idx

    @dead_time.setter
    def dead_time(self, dead_time):
        _ = ParamChecker(dead_time, "Stimulus dead time").not_empty.number.positive

        if float(dead_time) >= self.signal_time:
            raise ValueError('"Stimulus dead time" should be less than signal time')

        self._dead_time = float(dead_time)
        self._dead_time_idx = int(self.dead_time * self.fs)

    @property
    def threshold_from(self):
        return self._threshold_from

    @threshold_from.setter
    def threshold_from(self, threshold_from):
        if threshold_from == "":
            self._threshold_from = -100 / 1000000
        else:
            _ = ParamChecker(threshold_from, "Stimulus threshold from").number

        self._threshold_from = float(threshold_from)

    @property
    def threshold_to(self):
        return self._threshold_to

    @threshold_to.setter
    def threshold_to(self, threshold_to):
        if threshold_to == "":
            self._threshold_to = calculate_min_voltage_of_signal(self.signal)
        else:
            self._threshold_to = float(ParamChecker(threshold_to, "Stimulus threshold to").number.value)
