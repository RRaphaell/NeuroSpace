from Modules.ParamChecker import ParamChecker
from Modules.Waveform import Waveform
from Modules.utils import calculate_min_voltage_of_signal, calculate_stimulus, filter_stimulus


class Stimulus(Waveform):
    def __init__(self,  dead_time, threshold_from, threshold_to, useless_stimulus = "", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dead_time = dead_time
        self.threshold_from = threshold_from
        self.threshold_to = threshold_to
        self.useless_stimulus = useless_stimulus

    @property
    def indexes(self):
        if not(self.useless_stimulus and len(self.useless_stimulus) >0):
            return calculate_stimulus(self.signal, self.threshold_from, self.dead_time_idx)
        stimuluses = calculate_stimulus(self.signal, self.threshold_from, self.dead_time_idx)
        return filter_stimulus(stimuluses, self.useless_stimulus, self.from_s, self.fs)

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
    def useless_stimulus(self):
        return self._useless_stimulus

    @useless_stimulus.setter
    def useless_stimulus(self, useless_stimulus):
        if useless_stimulus == "":
            self._useless_stimulus = "" 
            return
        useless_stimulus_int = []
        for i in range(0,len(useless_stimulus)):
            useless_stimulus_temp = useless_stimulus[i]
            _ = ParamChecker(useless_stimulus_temp[0], "Useless Stimulus").number.positive
            _ = ParamChecker(useless_stimulus_temp[1], "Useless Stimulus").number.positive
            temp_from = float(useless_stimulus_temp[0])
            temp_to = float(useless_stimulus_temp[1])
            if float(temp_from) >= self.signal_time or float(temp_to) >= self.signal_time:
                raise ValueError('"useless stimulus times" should be less than signal time')
            useless_stimulus_int.append((temp_from, temp_to))
        self._useless_stimulus = useless_stimulus_int

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
