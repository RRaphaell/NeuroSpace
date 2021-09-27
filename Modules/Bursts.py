from Modules.ParamChecker import ParamChecker
from Modules.utils import calculate_bursts


class Bursts:
    def __init__(self, spikes_together_obj, burst_max_start="",
                 burst_max_end="", burst_betw="", burst_dur="",
                 burst_numb=""):
        self.spike_together_obj = spikes_together_obj
        self.burst_max_start = burst_max_start
        self.burst_max_end = burst_max_end
        self.burst_betw = burst_betw
        self.burst_dur = burst_dur
        self.burst_numb = burst_numb
    
    @property
    def bursts_colored(self):
        colored_bursts = []
        for spikes, color in self.spike_together_obj.spike_labels:
            bursts_starts, bursts_ends = calculate_bursts(spikes, self.burst_max_start, self.burst_max_end,
                                                          self.burst_betw, self.burst_dur, self.burst_numb)
            colored_bursts.append(([bursts_starts, bursts_ends], color))
        return colored_bursts

    @property
    def bursts_colored_indexes(self):
        colored_bursts = self.bursts_colored
        bursts_indexes = []
        for burst, color in colored_bursts:
            burst_start, burst_end = burst
            burst_start = [int(temp_start*self.spike_together_obj.fs) for temp_start in burst_start]
            burst_end = [int(temp_end*self.spike_together_obj.fs) for temp_end in burst_end]
            bursts_indexes.append(([burst_start, burst_end], color))
        return bursts_indexes

    # TODO:
    @property
    def bursts_indexes(self):
        bursts_start, bursts_ends = self.bursts
        bursts_start_idx = list(map(lambda x: int(x*self.spike_together_obj.fs), bursts_start))
        bursts_end_idx = list(map(lambda x: int(x*self.spike_together_obj.fs), bursts_ends))
        return bursts_start_idx, bursts_end_idx

    @property
    def burst_max_start(self):
        return self._burst_max_start
    
    @burst_max_start.setter
    def burst_max_start(self, burst_max_start):
        self._burst_max_start = ParamChecker(burst_max_start, "burst max start").not_empty.number.positive.value

    @property
    def burst_max_end(self):
        return self._burst_max_end
    
    @burst_max_end.setter
    def burst_max_end(self, burst_max_end):
        self._burst_max_end = ParamChecker(burst_max_end, "burst max end").not_empty.number.positive.value

    @property
    def burst_betw(self):
        return self._burst_betw
    
    @burst_betw.setter
    def burst_betw(self, burst_betw):
        self._burst_betw = ParamChecker(burst_betw, "burst betw").not_empty.number.positive.value

    @property
    def burst_dur(self):
        return self._burst_dur
    
    @burst_dur.setter
    def burst_dur(self, burst_dur):
        self._burst_dur = ParamChecker(burst_dur, "burst dur").not_empty.number.positive.value

    @property
    def burst_numb(self):
        return self._burst_numb
    
    @burst_numb.setter
    def burst_numb(self, burst_numb):
        self._burst_numb = int(ParamChecker(burst_numb, "burst numb").not_empty.number.positive.value)

