from Modules.utils import extract_signal, filter_base_frequency, plot_signal, get_signal_and_time


class Waveform:

    def __init__(self, electrode_stream, channels, canvas, from_s="", to_s="", high_pass="", low_pass=""):
        self._electrode_stream = electrode_stream
        self._channels = list(map(int, channels))
        self._fs = int(self._electrode_stream.channel_infos[0].sampling_frequency.magnitude)
        self._signal_time = electrode_stream.channel_data.shape[1] / self.fs
        self.from_s = from_s
        self.to_s = to_s
        self._signal, self._signal_time_range = self.get_signal()
        self.high_pass = high_pass
        self.low_pass = low_pass
        self._canvas = canvas

    @property
    def signal(self):
        return self._signal

    @property
    def fs(self):
        return self._fs

    @property
    def from_s(self):
        return self._from_s

    @from_s.setter
    def from_s(self, from_s):
        from_s = 0 if from_s == "" else from_s
        if not Waveform.is_number(from_s):
            raise ValueError ('"From" should be number')
        from_s = float(from_s)

        if not ((from_s >= 0) and (from_s < self._signal_time)):
            raise ValueError('"From" should be positive')
        self._from_s = from_s
        self._from_idx = int(self.from_s * self.fs)

    @property
    def to_s(self):
        return self._to_s

    @to_s.setter
    def to_s(self, to_s):
        to_s = self._signal_time if to_s == "" else to_s
        if not Waveform.is_number(to_s):
            raise ValueError('"To" should be number')
        to_s = float(to_s)

        if not ((to_s > 0) and (to_s <= self._signal_time)):
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
        elif not Waveform.is_number(high_pass):
            raise ValueError('"High pass" should be number')
        elif int(high_pass) < 0:
            raise ValueError('"High pass" should be positive')
        else:
            self._high_pass = int(high_pass)

    @property
    def low_pass(self):
        return self._low_pass

    @low_pass.setter
    def low_pass(self, low_pass):
        if low_pass == "":
            self._low_pass = None
        elif not Waveform.is_number(low_pass):
            raise ValueError('"Low pass" should be number')
        elif int(low_pass) < 0:
            raise ValueError('"Low pass" should be positive')
        elif int(low_pass) < self.high_pass:
            raise ValueError('"Low pass" should be greater than High pass')
        else:
            self._low_pass = int(low_pass)

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

    @staticmethod
    def is_number(x):
        try:
            float(x)
            return True
        except ValueError:
            return None
    
    def get_signal(self):
        return get_signal_and_time(self._electrode_stream, self._channels, self.fs, self._from_idx, self._to_idx)

    def get_filtered_signal(self):
        filtered_signal = filter_base_frequency(self.signal, self.fs, self.high_pass, self.low_pass)
        return filtered_signal

    def plot_waveform(self, ax_idx):
        filtered_signal = self.get_filtered_signal()
        plot_signal(filtered_signal, self._signal_time_range, self._canvas, ax_idx, "Time (seconds)", "Signal (uV)")

    def extract_signal(self, file_save_path):
        signal, time = self.get_signal()
        extract_signal(signal,time,file_save_path)
