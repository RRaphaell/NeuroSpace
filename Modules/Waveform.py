from Modules.utils import filter_base_frequency, plot_signal
from Modules.scripts import get_signal_time


class Waveform:

    def __init__(self, electrode_stream, fs, ch, canvas, high_pass=None, low_pass=None, from_s=None, to_s=None):
        self._electrode_stream = electrode_stream
        self._fs = int(self._electrode_stream.channel_infos[0].sampling_frequency.magnitude)
        self.from_s = 0 if from_s is None else from_s
        self._signal, self._signal_time = get_signal_time(self._electrode_stream, ch, self.from_s, to_s)
        self.to_s = len(self.signal) / fs if to_s is None else to_s
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
        if not (Waveform.is_number(self.from_s) and self.from_s > 0):
            raise ValueError('"From" should ne positive')
        self._from_s = from_s
        self._from_idx = int(self.from_s * self.fs)

    @property
    def to_s(self):
        return self._to_s

    @to_s.setter
    def to_s(self, to_s):
        if not (Waveform.is_number(self.to_s) and self.to_s > 0):
            raise ValueError('"To" should be positive')
        self._to_s = to_s
        self._to_idx = int(self.to_s * self.fs)

    @property
    def high_pass(self):
        return self._high_pass

    @high_pass.setter
    def high_pass(self, high_pass):
        if not (self.high_pass is None or Waveform.is_number(self.high_pass)):
            raise ValueError('"high_pass" should be integer')
        self._high_pass = high_pass

    @property
    def low_pass(self):
        return self._low_pass

    @low_pass.setter
    def low_pass(self, low_pass):
        if not (self.low_pass is None or Waveform.is_number(self.low_pass)):
            raise ValueError('"low_pass" should be integer')
        self._low_pass = low_pass

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
        except ValueError:
            return None

    def get_processed_signal(self, from_idx, to_idx):
        filtered_signal = filter_base_frequency(self.signal, self.fs, self.high_pass, self.low_pass)
        return filtered_signal[from_idx, to_idx]

    def plot_waveform(self):
        filtered_signal = self.get_processed_signal()
        plot_signal(filtered_signal, "Waveform", self._signal_time, self._canvas)
