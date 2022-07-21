import numpy

from Modules.ParamChecker import ParamChecker
from Modules.Spikes import Spikes
from Modules.utils import get_signal_cutouts, get_pca_labels, get_spikes_with_labels


class SpikeTogether(Spikes):
    """
    SpikeTogether module is to give us the cutout waveforms (pre-spike : spike-post)
    The idea of this class is that observing the waveforms of spikes are important to determine how neurons behave.

    Attributes:
        pre (float): time before spike for cutouts
        post (float): time after spike for cutouts
        component_number (int): the possible quantity of neurons who spike
        cutouts (list -> numpy.ndarray -> numpy.float64): signal parts arnd spikes, len of cutouts is len of spikes_idx
        labels (numpy.ndarray -> numpy.int64): the labels of spikes, the len of this should be the len of spikes
        spike_labels_indexes (list -> tuple): color and the corresponding spike indices
        spike_labels (list -> tuple): color and the corresponding spike times

    Args:
        pre (str): time before spike for cutouts
        post (str): time after spike for cutouts
        component_number (str): the possible quantity of neurons who spike

    Note that *args and **kwargs are defined in the parent class
    """
    def __init__(self,  pre, post, component_number, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pre = pre
        self.post = post
        self.component_number = component_number
        self._cutouts = get_signal_cutouts(self.signal * 1000_000, self.fs, self.indexes, self.pre, self.post)

    @property
    def pre(self) -> float:
        return self._pre

    @pre.setter
    def pre(self, value: str) -> None:
        self._pre = ParamChecker(value, "Pre").not_empty.number.positive.value

    @property
    def post(self) -> float:
        return self._post

    @post.setter
    def post(self, value: str) -> None:
        self._post = ParamChecker(value, "Post").not_empty.number.positive.value

    @property
    def component_number(self) -> int:
        return self._component_number

    @component_number.setter
    def component_number(self, value: str) -> None:
        self._component_number = int(ParamChecker(value, "Component number").not_empty.number.positive.value)

    @property
    def cutouts(self) -> list:
        return self._cutouts

    # TODO:
    @property
    def labels(self) -> numpy.ndarray:
        """
        this function calls the pca function from utils.py which predicts labels for spikes with the waveform features
        it returns [0] if there is only one cutout because pca can't predict the labels for only one example

        Returns:
            labels (numpy.ndarray -> numpy.int64): the labels of spikes, len of this should be the len of spikes

        """
        if not len(self.cutouts):
            return numpy.array()
        elif len(self.cutouts) == 1:
            return numpy.array([0])
        labels = get_pca_labels(self.cutouts, self.component_number)
        return labels

    @property
    def spike_labels_indexes(self) -> list:
        """
        this function matches spikes to their colors

        Returns:
            spike_labels_indexes (list -> tuple): color and the corresponding spike indices

        """
        if not len(self.cutouts):
            return []
        return get_spikes_with_labels(self.labels, self.indexes)

    @property
    def spike_labels(self) -> list:
        """
        this function matches spikes to their colors and returns spike times and colors.

        Returns:
            spike_labels (list -> tuple): color and the corresponding spike times

        """
        if not len(self.cutouts):
            return []
        spikes_times_labels = []
        spikes_with_labels = get_spikes_with_labels(self.labels, self.indexes)
        for spikes, color in spikes_with_labels:
            spikes = [i/self.fs for i in spikes]
            spikes_times_labels.append((spikes, color))
        return spikes_times_labels
