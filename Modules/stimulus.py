import numpy

from Modules.ParamChecker import ParamChecker
from Modules.Waveform import Waveform
from Modules.utils import calculate_min_voltage_of_signal, calculate_stimulus, filter_stimulus


class Stimulus(Waveform):
    """
    Stimulus class is to detect artificial stimulus.
    This class is useful when recordings don't include such information.
    If your electrode_stream provides stimulus information too,
    we recommend using that one because that will be 100% accurate.
    But in case you don't have that, this class will help you a lot.

    Attributes:
        dead_time (float): after we find stimulus, during DEAD_TIME, we shouldn't search for next one
        threshold_from (float): the pre-defined max/min(depends on if signal is negative or not) value of signal
                                to detect stimulus
        threshold_to (float): the pre-defined max/min(depends on if signal is negative or not) value of signal
                              to detect stimulus
        useless_stimulus (list): user's provided ranges where we should not search for stimulus
        indexes (list): corresponding indexes of detected stimulus times
        time_range (list): detected stimulus times
        dead_time_idx (int): corresponding index of dead_time


    Args:
        dead_time (str): after we find stimulus, during DEAD_TIME, we shouldn't search for next one
        threshold_from (str): the pre-defined max/min(depends on if signal is negative or not) value of signal
                              to detect stimulus
        threshold_to (str): the pre-defined max/min(depends on if signal is negative or not) value of signal
                            to detect stimulus
        useless_stimulus (str): user's provided ranges where we should not search for stimulus

    Note that *args and **kwargs are defined in the parent class
    """
    def __init__(self,  dead_time, threshold_from, threshold_to, useless_stimulus="", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dead_time = dead_time
        self.threshold_from = threshold_from
        self.threshold_to = threshold_to
        self.useless_stimulus = useless_stimulus

    @property
    def indexes(self) -> numpy.ndarray:
        """
        this function calculates stimulus with algorithm which is provided and explained in utils.py
        after that if user wanted specific filtering, it filters the stimulus.

        Returns:
            stimulus (numpy.ndarray): filtered detected stimulus times

        """
        if not(self.useless_stimulus and len(self.useless_stimulus) >0):
            return calculate_stimulus(self.signal, self.threshold_from, self.dead_time_idx)
        stimulus = calculate_stimulus(self.signal, self.threshold_from, self.dead_time_idx)
        return filter_stimulus(stimulus, self.useless_stimulus, self.from_s, self.fs)

    @property
    def time_range(self) -> numpy.ndarray:
        """
        this function calculates corresponding indexes such that it divides the values by sampling frequency

        Returns:
            indexes (numpy.ndarray): corresponding indexes for detected stimulus times
        """
        indexes = self.indexes
        if len(indexes) > 1:
            time_range = indexes/self.fs + self.from_s
            return time_range
        return indexes

    @property
    def dead_time(self) -> float:
        return self._dead_time

    @property
    def dead_time_idx(self) -> int:
        return self._dead_time_idx

    @dead_time.setter
    def dead_time(self, dead_time: str) -> None:
        _ = ParamChecker(dead_time, "Stimulus dead time").not_empty.number.positive

        if float(dead_time) >= self.signal_time:
            raise ValueError('"Stimulus dead time" should be less than signal time')

        self._dead_time = float(dead_time)
        self._dead_time_idx = int(self.dead_time * self.fs)

    @property
    def useless_stimulus(self) -> list:
        return self._useless_stimulus

    @useless_stimulus.setter
    def useless_stimulus(self, useless_stimulus: str) -> None:
        """
        application user provides useless_stimulus ranges like this : "1-15, 16-17"
        these are ranges we need to translate on "float language".
        f.e for above-mentioned example, result of this function would be: [(1,15), (16,17)]

        Args:
            useless_stimulus (str): user's provided ranges where we should not search for stimulus
        """
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
    def threshold_from(self) -> float:
        return self._threshold_from

    @threshold_from.setter
    def threshold_from(self, threshold_from: str) -> None:
        """
        this setter method checks and casts threshold value if it is provided
        else makes that -0.0001 (TODO: Needs to be remembered why is that specific value)

        Args:
            threshold_from (str): the pre-defined max/min(depends on if signal is negative or not) value of signal
                                to detect stimulus
        """

        if threshold_from == "":
            self._threshold_from = -100 / 1000000
        else:
            _ = ParamChecker(threshold_from, "Stimulus threshold from").number

        self._threshold_from = float(threshold_from)

    @property
    def threshold_to(self) -> float:
        return self._threshold_to

    @threshold_to.setter
    def threshold_to(self, threshold_to: str) -> None:
        """
        this setter method checks and casts threshold value if it is provided
        else makes that a min voltage value of signal

        Args:
            threshold_to (str): the pre-defined max/min(depends on if signal is negative or not) value of signal
                                to detect stimulus
        """
        if threshold_to == "":
            self._threshold_to = calculate_min_voltage_of_signal(self.signal)
        else:
            self._threshold_to = float(ParamChecker(threshold_to, "Stimulus threshold to").number.value)
