from Modules.utils import calculate_min_voltage_of_signal, calculate_spikes, calculate_threshold_based_on_signal, is_number
from Modules.Waveform import Waveform
from Widgets.WaveformWidget import WaveformWidget


class Spikes(Waveform):

    def __init__(self, electrode_stream, channels, spike_dead_time, stimulus_ticked, burst_ticked,
                                    spike_threshold_from="", spike_threshold_to="",
                                    stimulus_dead_time="", stimulus_threshold_from="",
                                    stimulus_threshold_to="", burst_max_start="",
                                    burst_max_end="", burst_betw="", burst_dur="",
                                    burst_numb="", from_s="", to_s="", high_pass="", low_pass=""):
        super().__init__(electrode_stream,channels,from_s,to_s,high_pass,low_pass)
        self.spike_dead_time = spike_dead_time
        self.stimulus_ticked = stimulus_ticked
        self.burst_ticked = burst_ticked
        self.spike_threshold_from = spike_threshold_from
        self.spike_threshold_to = spike_threshold_to
        self.stimulus_dead_time = stimulus_dead_time
        self.stimulus_threshold_from = stimulus_threshold_from
        self.stimulus_threshold_to = stimulus_threshold_to
        self.burst_max_start = burst_max_start
        self.burst_max_end = burst_max_end
        self.burst_betw = burst_betw
        self.burst_dur = burst_dur
        self.burst_numb = burst_numb
        self._dead_time_idx = None
    
    @property
    def spike_dead_time(self):
        return self.spike_dead_time
    
    @spike_dead_time.setter
    def spike_dead_time(self, spike_dead_time):
        if not is_number(spike_dead_time):
            raise ValueError ('"Spikes dead time" should be number')

        if not ((spike_dead_time >= 0) and (spike_dead_time < self.signal_time)):
            raise ValueError('"Spikes dead time" should be positive')
        self.spike_dead_time = spike_dead_time
        self._dead_time_idx = int(self.spike_dead_time*self.fs)

    @property
    def spike_threshold_from(self):
        return self.spike_threshold_from
    
    @spike_threshold_from.setter
    def spike_threshold_from(self, spike_threshold_from):
        if spike_threshold_from == "":
            self.spike_threshold_from = calculate_threshold_based_on_signal(self.signal)
        elif not is_number(spike_threshold_from):
            raise ValueError ('"Spikes Threshold from" should be number')
        elif not ((spike_threshold_from >= 0)):
            raise ValueError('"Spikes Threshold from" should be positive')
        self.spike_threshold_from = spike_threshold_from

    @property
    def spike_threshold_to(self):
        return self.spike_threshold_to
    
    @spike_threshold_to.setter
    def spike_threshold_to(self, spike_threshold_to):
        if spike_threshold_to == "":
            self.spike_threshold_to = calculate_min_voltage_of_signal(self.signal)
        else:
            self.spike_threshold_to = self.threshold_to_checker(spike_threshold_to)

    @property
    def stimulus_dead_time(self):
        return self.stimulus_dead_time
    
    @stimulus_dead_time.setter
    def stimulus_dead_time(self, stimulus_dead_time):
        if self.stimulus_ticked and not is_number(stimulus_dead_time):
            raise ValueError ('"Stimulus dead time " should be number')
        elif self.stimulus_ticked and not ((stimulus_dead_time >= 0)):
            raise ValueError('"Stimulus dead time " should be positive')
        self.stimulus_dead_time = stimulus_dead_time

    @property
    def stimulus_threshold_from(self):
        return self.stimulus_threshold_from
    
    @stimulus_threshold_from.setter
    def stimulus_threshold_from(self, stimulus_threshold_from):
        if self.stimulus_ticked and stimulus_threshold_from == "":
            self.stimulus_threshold_from = -100/1000000
        elif self.stimulus_ticked and not is_number(stimulus_threshold_from):
            raise ValueError ('"Stimulus Threshold from" should be number')
        elif self.stimulus_ticked and not ((stimulus_threshold_from >= 0)):
            raise ValueError('"Stimulus Threshold from" should be positive')
        self.stimulus_threshold_from = stimulus_threshold_from
    
    @property
    def stimulus_threshold_to(self):
        return self.stimulus_threshold_to
    
    @stimulus_threshold_to.setter
    def stimulus_threshold_to(self, stimulus_threshold_to):
        if self.stimulus_ticked and stimulus_threshold_to == "":
            self.stimulus_threshold_to = calculate_min_voltage_of_signal(self.signal)
        elif stimulus_threshold_to != "":
            self.stimulus_threshold_to = self.threshold_to_checker(stimulus_threshold_to)
        else :
            self.stimulus_threshold_to = ""
    @property
    def burst_max_start(self):
        return self.burst_max_start
    
    @burst_max_start.setter
    def burst_max_start(self, burst_max_start):
        self,burst_max_start = self.burst_param_check(burst_max_start, "burst max start")

    @property
    def burst_max_end(self):
        return self.burst_max_end
    
    @burst_max_end.setter
    def burst_max_end(self, burst_max_end):
        self,burst_max_end = self.burst_param_check(burst_max_end, "burst max end")

    @property
    def burst_betw(self):
        return self.burst_betw
    
    @burst_betw.setter
    def burst_betw(self, burst_betw):
        self,burst_betw = self.burst_param_check(burst_betw, "burst betw")

    @property
    def burst_dur(self):
        return self.burst_dur
    
    @burst_dur.setter
    def burst_dur(self, burst_dur):
        self,burst_dur = self.burst_param_check(burst_dur, "burst dur")

    @property
    def burst_numb(self):
        return self.burst_numb
    
    @burst_numb.setter
    def burst_numb(self, burst_numb):
        self,burst_numb = self.burst_param_check(burst_numb, "burst numb")


    @property
    def _dead_time_idx(self):
        return self._dead_time_idx

    @_dead_time_idx.setter
    def _dead_time_idx(self, _dead_time_idx):
        self._dead_time_idx = _dead_time_idx

    def burst_param_check(self, param, param_name):
        if self.burst_ticked and not is_number(param):
            return ValueError (f'"{param_name}" should be number')
        elif self.burst_ticked and not ((param >= 0)):
            return ValueError(f'"{param_name}" should be positive')
        return param
    
    def threshold_checker(self, threshold):
        if self.stimulus_ticked and not is_number(threshold):
            raise ValueError ('"Threshold " should be number')
        elif self.stimulus_ticked and not ((threshold >= 0)):
            raise ValueError('"Threshold " should be positive')
        return threshold

    def get_spikes(self):
        signal = self.get_filtered_signal()
        return calculate_spikes(signal, self.spike_threshold_from, self.spike_threshold_to, self.spike_dead_time)
        