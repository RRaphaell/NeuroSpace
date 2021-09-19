from Modules.utils import (convert_channel_label_to_id
                           , filter_base_frequency
                           , get_signal_and_time
                           , round_to_closest
                           , is_number)


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
        self._signal_time_range = None, None

    @property
    def signal(self):
        return self._get_filtered_signal()

    @property
    def _signal(self):
        signal, time = get_signal_and_time(self._electrode_stream, self._channels, self.fs, self._from_idx, self._to_idx)
        self._signal_time_range = time
        return signal

    @property
    def signal_time_range(self):
        return self._signal_time_range

    @property
    def fs(self):
        return self._fs

    @property
    def from_s(self):
        return self._from_s

    @from_s.setter
    def from_s(self, from_s):
        from_s = 0 if from_s == "" else from_s
        if not is_number(from_s):
            raise ValueError('"From" should be number')
        from_s = round_to_closest(float(from_s), 1/self.fs)

        if not ((from_s >= 0) and (from_s < self.signal_time)):
            raise ValueError('"From" should be positive')
        self._from_s = from_s
        self._from_idx = int(self.from_s * self.fs)

    @property
    def to_s(self):
        return self._to_s

    @to_s.setter
    def to_s(self, to_s):
        to_s = self.signal_time if to_s == "" else to_s
        if not is_number(to_s):
            raise ValueError('"To" should be number')
        to_s = round_to_closest(float(to_s), 1/self.fs)

        if not ((to_s > 0) and (to_s <= self.signal_time)):
            raise ValueError('"To" should be positive')

        if to_s <= self.from_s:
            raise ValueError('"To" should be greater than "from"')

        self._to_s = to_s
        self._to_idx = int(self.to_s * self.fs)

    @property
    def high_pass(self):
        return self._high_pass

    @high_pass.setter
    def high_pass(self, high_pass):
        if high_pass == "":
            self._high_pass = None
        elif not is_number(high_pass):
            raise ValueError('"High pass" should be number')
        elif int(float(high_pass)) < 0:
            raise ValueError('"High pass" should be positive')
        else:
            self._high_pass = int(float(high_pass))

    @property
    def low_pass(self):
        return self._low_pass

    @low_pass.setter
    def low_pass(self, low_pass):
        if low_pass == "":
            self._low_pass = None
        elif not is_number(low_pass):
            raise ValueError('"Low pass" should be number')
        elif int(float(low_pass)) < 0:
            raise ValueError('"Low pass" should be positive')
        elif self.high_pass and int(float(low_pass)) < self.high_pass:
            raise ValueError('"Low pass" should be greater than High pass')
        else:
            self._low_pass = int(float(low_pass))

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
        filtered_signal = filter_base_frequency(self._signal, self.fs, self.high_pass, self.low_pass)
        return filtered_signal
