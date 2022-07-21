import numpy
import numpy as np
from typing import List
from Modules.ParamChecker import ParamChecker
from Modules.utils import (convert_channel_label_to_id
                           , filter_base_frequency
                           , get_signal
                           , round_to_closest)


class Waveform:
    """
    Waveform class is to make signal's main, waveform object usable
    It firstly reads the signal (if there is more than one channel, averages it)
    and in case of high_pass and low_pass filters, gives us filtered one.

    Attributes:
        signal_time (float): recording's time in seconds
        from_s (float): user's chosen start time in seconds (None indicates zero)
        to_s (float): user's chosen end time in seconds (None indicates the length of signal)
        high_pass (int): user's chosen filter (every frequency higher than that number will remain)
        low_pass (int): user's chosen filter (every frequency lower than that number will remain)

    Args:
        electrode_stream (McsPy.McsData.AnalogStream): the main data object of the recording
        channels (list -> str): make all of the crazy calculations.user's chosen channels to get signal
        from_s (str): user's chosen start time in seconds (None indicates zero)
        to_s (str): user's chosen end time in seconds (None indicates the length of signal)
        high_pass (str): user's chosen filter (every frequency higher than that number will remain)
        low_pass (str): user's chosen filter (every frequency lower than that number will remain)
    """
    def __init__(self, electrode_stream,
                 channels: List[str], from_s: str = "", to_s: str = "", high_pass: str = "", low_pass: str = ""):
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
    def signal(self) -> numpy.ndarray:
        return self._signal

    @property
    def _signal_in_range(self) -> numpy.ndarray:
        return get_signal(self._electrode_stream, self._channels, self._from_idx, self._to_idx)

    @property
    def time(self) -> numpy.ndarray:
        return np.array(range(self._from_idx, self._to_idx + 1)) / self._fs

    @property
    def fs(self) -> int:
        return self._fs

    @property
    def from_s(self) -> float:
        return self._from_s

    @from_s.setter
    def from_s(self, from_s: str) -> None:
        """
        Firstly checks the user's input from_s and then rounds it to the closest signal existing timestamp

        Args:
            from_s (str): signals desired start time
        """
        from_s = 0 if from_s == "" else from_s
        from_s = round_to_closest(ParamChecker(from_s, "From").number.positive.value, 1/self.fs)

        if not ((from_s >= 0) and (from_s < self.signal_time)):
            raise ValueError('Parameter "From" should be less than length of signal')
        self._from_s = from_s
        self._from_idx = int(self.from_s * self.fs)

    @property
    def to_s(self) -> float:
        return self._to_s

    @to_s.setter
    def to_s(self, to_s: str) -> None:
        """
        Firstly checks the user's input to_s and then rounds it to the closest signal existing timestamp

        Args:
            to_s (str): signals desired end time
        """
        to_s = self.signal_time if to_s == "" else to_s
        to_s = round_to_closest(ParamChecker(to_s, "To").number.positive.value, 1/self.fs)

        if not ((to_s > 0) and (to_s <= self.signal_time)):
            raise ValueError('Parameter "To" should be less than length of signal')

        if to_s <= self.from_s:
            raise ValueError('Parameter "To" should be greater than parameter "From"')

        self._to_s = to_s
        self._to_idx = int(self.to_s * self.fs)

    @property
    def high_pass(self) -> int:
        return self._high_pass

    @high_pass.setter
    def high_pass(self, high_pass: str) -> None:
        """
        Firstly checks the user's input and then casts it as an integer

        Args:
            high_pass (str): every frequency higher than that number will remain after filter
        """
        if high_pass == "":
            self._high_pass = None
        else:
            self._high_pass = int(ParamChecker(high_pass, "High pass").number.positive.value)

    @property
    def low_pass(self) -> int:
        return self._low_pass

    @low_pass.setter
    def low_pass(self, low_pass: str) -> None:
        """
        Firstly checks the user's input and then casts it as an integer, it also checks if the
        low_pass number is greater than high pass or not. it is important because,
        if that condition is not satisfied, zero frequency will remain in the signal.

        Args:
            low_pass (str): every frequency higher than that number will remain after filter
        """
        if low_pass == "":
            self._low_pass = None
        else:
            low_pass_checked = ParamChecker(low_pass, "Low pass").number.positive.value
            if self.high_pass and int(low_pass_checked) < self.high_pass:
                raise ValueError('Parameter "Low pass" should be greater than parameter "High pass"')

            self._low_pass = int(low_pass_checked)

    @property
    def _from_idx(self) -> int:
        return self.__from_idx

    @_from_idx.setter
    def _from_idx(self, from_idx: int) -> None:
        self.__from_idx = from_idx

    @property
    def _to_idx(self) -> int:
        return self.__to_idx

    @_to_idx.setter
    def _to_idx(self, to_idx: int) -> None:
        self.__to_idx = to_idx

    def _get_filtered_signal(self) -> numpy.ndarray:
        """
        Firstly checks the user's input and then casts it as an integer, it also checks if the
        low_pass number is greater than high pass or not. it is important because,
        if that condition is not satisfied, zero frequency will remain in the signal.

        Returns:
            filtered_signal (numpy.ndarray): filtered signal, if high_pass and low_pass is none, signal will remain same
        """
        filtered_signal = filter_base_frequency(self._signal_in_range, self.fs, self.high_pass, self.low_pass)
        return filtered_signal
