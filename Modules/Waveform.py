import numpy as np
from Modules.ParamChecker import ParamChecker
from Modules.utils import (convert_channel_label_to_id
                           , filter_base_frequency
                           , get_signal
                           , round_to_closest)


class Waveform:
    def __init__(self, electrode_stream, channels, from_s="", to_s="", high_pass="", low_pass=""):
        self._electrode_stream = electrode_stream
        self._channels = list(map(lambda ch: convert_channel_label_to_id(electrode_stream, ch), channels))
        self._fs = int(self._electrode_stream.channel_infos[0].sampling_frequency.magnitude)
        self.signal_time = (electrode_stream.channel_data.shape[1]-1) / self.fs
        self._from_idx, self._to_idx = None, None
        self.from_s, self.to_s = from_s, to_s
        self.high_pass = high_pass
        self.low_pass = low_pass

        self._signal = self._get_filtered_signal()

    @property
    def signal(self):
        return self._signal

    @property
    def _signal_in_range(self):
        return get_signal(self._electrode_stream, self._channels, self._from_idx, self._to_idx)

    @property
    def time(self):
        return np.array(range(self._from_idx, self._to_idx + 1)) / self._fs

    @property
    def fs(self):
        return self._fs

    @property
    def from_s(self):
        return self._from_s

    @from_s.setter
    def from_s(self, from_s):
        from_s = 0 if from_s == "" else from_s
        from_s = round_to_closest(ParamChecker(from_s, "From").number.positive.value, 1/self.fs)

        if not ((from_s >= 0) and (from_s < self.signal_time)):
            raise ValueError('Parameter "From" should be less than length of signal')
        self._from_s = from_s
        self._from_idx = int(self.from_s * self.fs)

    @property
    def to_s(self):
        return self._to_s

    @to_s.setter
    def to_s(self, to_s):
        to_s = self.signal_time if to_s == "" else to_s
        to_s = round_to_closest(ParamChecker(to_s, "To").number.positive.value, 1/self.fs)

        if not ((to_s > 0) and (to_s < self.signal_time)):
            raise ValueError('Parameter "To" should be less than length of signal')

        if to_s <= self.from_s:
            raise ValueError('Parameter "To" should be greater than parameter "From"')

        self._to_s = to_s
        self._to_idx = int(self.to_s * self.fs)

    @property
    def high_pass(self):
        return self._high_pass

    @high_pass.setter
    def high_pass(self, high_pass):
        if high_pass == "":
            self._high_pass = None
        else:
            self._high_pass = int(ParamChecker(high_pass, "High pass").number.positive.value)

    @property
    def low_pass(self):
        return self._low_pass

    @low_pass.setter
    def low_pass(self, low_pass):
        if low_pass == "":
            self._low_pass = None
        else:
            low_pass_checked = ParamChecker(low_pass, "Low pass").number.positive.value
            if self.high_pass and int(low_pass_checked) < self.high_pass:
                raise ValueError('Parameter "Low pass" should be greater than parameter "High pass"')

            self._low_pass = int(low_pass_checked)

    @property
    def _from_idx(self):
        return self.__from_idx

    @_from_idx.setter
    def _from_idx(self, from_idx):
        self.__from_idx = from_idx

    @property
    def _to_idx(self):
        return self.__to_idx

    @_to_idx.setter
    def _to_idx(self, to_idx):
        self.__to_idx = to_idx

    def _get_filtered_signal(self):
        filtered_signal = filter_base_frequency(self._signal_in_range, self.fs, self.high_pass, self.low_pass)
        return filtered_signal
