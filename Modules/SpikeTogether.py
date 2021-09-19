from Modules.Spikes import Spikes
from Modules.utils import get_signal_cutouts, get_pca_labels, is_number


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
        SpikeTogether.valid_param(value, "pre")
        self._pre = float(value)

    @property
    def post(self):
        return self._post

    @post.setter
    def post(self, value):
        SpikeTogether.valid_param(value, "post")
        self._post = float(value)

    @property
    def component_number(self):
        return self._component_number

    @component_number.setter
    def component_number(self, value):
        SpikeTogether.valid_param(value, "component number")
        self._component_number = int(value)

    @property
    def cutouts(self):
        return self._cutouts

    @property
    def labels(self):
        if not len(self.cutouts):
            return []

        labels = get_pca_labels(self.cutouts, self.component_number)
        return labels

    @staticmethod
    #  check if value is not empty and also positive integer
    def valid_param(value, param_name):
        if value == "":
            raise ValueError(f'please enter {param_name} value')
        elif not is_number(value):
            raise ValueError(f'{param_name} should be number')
        elif not (int(float(value)) >= 0):
            raise ValueError(f'{param_name} should be positive')

