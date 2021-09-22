from Modules.ParamChecker import ParamChecker
from Modules.Spikes import Spikes
from Modules.utils import get_signal_cutouts, get_pca_labels


class SpikeTogether(Spikes):

    def __init__(self,  pre, post, component_number, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pre = pre
        self.post = post
        self.component_number = component_number
        self._cutouts = get_signal_cutouts(self.signal*1000_000, self.fs, self.spikes_indexes, self.pre, self.post)

    @property
    def pre(self):
        return self._pre

    @pre.setter
    def pre(self, value):
        self._pre = ParamChecker(value, "pre").not_empty.positive.value

    @property
    def post(self):
        return self._post

    @post.setter
    def post(self, value):
        self._post = ParamChecker(value, "post").not_empty.positive.value

    @property
    def component_number(self):
        return self._component_number

    @component_number.setter
    def component_number(self, value):
        self._component_number = int(ParamChecker(value, "component number").not_empty.positive.value)

    @property
    def cutouts(self):
        return self._cutouts

    @property
    def labels(self):
        if not len(self.cutouts):
            return []

        labels = get_pca_labels(self.cutouts, self.component_number)
        return labels
