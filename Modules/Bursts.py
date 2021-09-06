
from Modules.utils import calculate_bursts, is_number


class Bursts:
    def __init__(self, spikes_obj, burst_max_start="",
                burst_max_end="", burst_betw="", burst_dur="",
                burst_numb=""):
        self._spikes_obj = spikes_obj
        self.burst_max_start = burst_max_start
        self.burst_max_end = burst_max_end
        self.burst_betw = burst_betw
        self.burst_dur = burst_dur
        self.burst_numb = burst_numb
    
    @property
    def bursts(self):
        return calculate_bursts(self._spikes_obj.spikes, self.burst_max_start, self.burst_max_end, 
                                self.burst_betw, self.burst_dur, self.burst_numb)

    @property
    def burst_max_start(self):
        return self._burst_max_start
    
    @burst_max_start.setter
    def burst_max_start(self, burst_max_start):
        self._burst_max_start = self.burst_param_check(burst_max_start, "burst max start")

    @property
    def burst_max_end(self):
        return self._burst_max_end
    
    @burst_max_end.setter
    def burst_max_end(self, burst_max_end):
        self._burst_max_end = self.burst_param_check(burst_max_end, "burst max end")

    @property
    def burst_betw(self):
        return self._burst_betw
    
    @burst_betw.setter
    def burst_betw(self, burst_betw):
        self._burst_betw = self.burst_param_check(burst_betw, "burst betw")

    @property
    def burst_dur(self):
        return self._burst_dur
    
    @burst_dur.setter
    def burst_dur(self, burst_dur):
        self._burst_dur = self.burst_param_check(burst_dur, "burst dur")

    @property
    def burst_numb(self):
        return self._burst_numb
    
    @burst_numb.setter
    def burst_numb(self, burst_numb):
        self._burst_numb = int(self.burst_param_check(burst_numb, "burst numb"))

    def burst_param_check(self, param, param_name):
        if  not is_number(param):
            return ValueError (f'"{param_name}" should be number')
        elif  not (float(param) >= 0):
            return ValueError(f'"{param_name}" should be positive')
        return float(param)