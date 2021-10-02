from Modules.ParamChecker import ParamChecker
from Modules.Spikes import Spikes
from Modules.utils import get_signal_cutouts, get_pca_labels, get_spikes_with_labels


class SpikeTogether(Spikes):

    def __init__(self,  pre, post, component_number, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pre = pre
        self.post = post
        self.component_number = component_number
        self._cutouts = get_signal_cutouts(self.signal * 1000_000, self.fs, self.indexes, self.pre, self.post)

    @property
    def pre(self):
        return self._pre

    @pre.setter
    def pre(self, value):
        self._pre = ParamChecker(value, "Pre").not_empty.number.positive.value

    @property
    def post(self):
        return self._post

    @post.setter
    def post(self, value):
        self._post = ParamChecker(value, "Post").not_empty.number.positive.value

    @property
    def component_number(self):
        return self._component_number

    @component_number.setter
    def component_number(self, value):
        self._component_number = int(ParamChecker(value, "Component number").not_empty.number.positive.value)

    @property
    def cutouts(self):
        return self._cutouts

    # TODO:
    @property
    def labels(self):
        if not len(self.cutouts):
            return []
        elif len(self.cutouts) == 1:
            return [0]
        labels = get_pca_labels(self.cutouts, self.component_number)
        return labels

    @property
    def spike_labels_indexes(self):
        if not len(self.cutouts):
            return []
        return get_spikes_with_labels(self.labels, self.indexes)

    @property
    def spike_labels(self):
        if not len(self.cutouts):
            return []
        spikes_times_labels = []
        spikes_with_labels = get_spikes_with_labels(self.labels, self.indexes)
        for spikes, color in spikes_with_labels:
            spikes = [i/self.fs for i in spikes]
            spikes_times_labels.append((spikes, color))
        return spikes_times_labels
