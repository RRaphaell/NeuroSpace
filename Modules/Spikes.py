from Modules.utils import (calculate_min_voltage_of_signal,
                           calculate_spikes,
                           calculate_threshold_based_on_signal,
                           is_number)
from Modules.Waveform import Waveform


class Spikes(Waveform):

    def __init__(self,  spike_dead_time, spike_threshold_from="",
                 spike_threshold_to="", *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.spike_dead_time = spike_dead_time
        self.spike_threshold_from = spike_threshold_from
        self.spike_threshold_to = spike_threshold_to
        # self.stimulus_dead_time = stimulus_dead_time
        # self.stimulus_threshold_from = stimulus_threshold_from
        # self.stimulus_threshold_to = stimulus_threshold_to
    
    @property
    def spikes_indexes(self):
        return calculate_spikes(self.signal, self.spike_threshold_from, self.spike_threshold_to, self.fs, self.dead_time_idx)

    @property
    def spikes_time_range(self):
        indexes = self.spikes_indexes
        if len(indexes) > 1 :
            time_range = indexes/self.fs + self.from_s
            return time_range
        return indexes

    @property
    def spike_dead_time(self):
        return self._spike_dead_time
    
    @spike_dead_time.setter
    def spike_dead_time(self, spike_dead_time):
        if not is_number(spike_dead_time):
            raise ValueError('"Spikes dead time" should be number')

        if not ((float(spike_dead_time) >= 0) and (float(spike_dead_time) < self.signal_time)):
            raise ValueError('"Spikes dead time" should be positive')
        self._spike_dead_time = float(spike_dead_time)
        self._dead_time_idx = int(self.spike_dead_time*self.fs)

    @property
    def spike_threshold_from(self):
        return self._spike_threshold_from
    
    @spike_threshold_from.setter
    def spike_threshold_from(self, spike_threshold_from):
        if spike_threshold_from == "":
            self._spike_threshold_from = calculate_threshold_based_on_signal(self.signal)
        elif not is_number(spike_threshold_from):
            raise ValueError('"Spikes Threshold from" should be number')
        elif not (int(float(spike_threshold_from)) >= 0):
            raise ValueError('"Spikes Threshold from" should be positive')
        self._spike_threshold_from = float(spike_threshold_from)

    @property
    def spike_threshold_to(self):
        return self._spike_threshold_to
    
    @spike_threshold_to.setter
    def spike_threshold_to(self, spike_threshold_to):
        if spike_threshold_to == "":
            self._spike_threshold_to = calculate_min_voltage_of_signal(self.signal)
        else:
            self._spike_threshold_to = Spikes.threshold_checker(spike_threshold_to)

    # @property
    # def stimulus_dead_time(self):
    #     return self._stimulus_dead_time
    
    # @stimulus_dead_time.setter
    # def stimulus_dead_time(self, stimulus_dead_time):
    #     if self.stimulus_ticked and not is_number(stimulus_dead_time):
    #         raise ValueError('"Stimulus dead time " should be number')
    #     elif self.stimulus_ticked and not (float(stimulus_dead_time) >= 0):
    #         raise ValueError('"Stimulus dead time " should be positive')
    #     self._stimulus_dead_time = float(stimulus_dead_time)

    # @property
    # def stimulus_threshold_from(self):
    #     return self._stimulus_threshold_from
    
    # @stimulus_threshold_from.setter
    # def stimulus_threshold_from(self, stimulus_threshold_from):
    #     if self.stimulus_ticked and stimulus_threshold_from == "":
    #         self._stimulus_threshold_from = -100/1000000
    #     elif self.stimulus_ticked and not is_number(stimulus_threshold_from):
    #         raise ValueError('"Stimulus Threshold from" should be number')
    #     elif self.stimulus_ticked and not (stimulus_threshold_from >= 0):
    #         raise ValueError('"Stimulus Threshold from" should be positive')
    #     self._stimulus_threshold_from = stimulus_threshold_from
    
    # @property
    # def stimulus_threshold_to(self):
    #     return self._stimulus_threshold_to
    
    # @stimulus_threshold_to.setter
    # def stimulus_threshold_to(self, stimulus_threshold_to):
    #     if self.stimulus_ticked and stimulus_threshold_to == "":
    #         self._stimulus_threshold_to = calculate_min_voltage_of_signal(self.signal)
    #     elif stimulus_threshold_to != "":
    #         self._stimulus_threshold_to = Spikes.threshold_checker(stimulus_threshold_to)
    #     else :
    #         self._stimulus_threshold_to = ""

    @property
    def dead_time_idx(self):
        return self._dead_time_idx

    @staticmethod
    def threshold_checker(threshold):
        if not is_number(threshold):
            raise ValueError('"Threshold " should be number')
        elif not (int(float(threshold)) >= 0):
            raise ValueError('"Threshold " should be positive')
        return float(threshold)
    