from Controllers.Controller import Controller
from Controllers.utils import catch_exception
from Modules.SpikeTogether import SpikeTogether
from Modules.utils import plot_spikes_together
from Widgets.SpikeTogetherWidget import SpikeTogetherWidget
from utils import get_default_widget


class SpikeTogetherController(Controller):
    def __init__(self, *args):
        self.view = SpikeTogetherWidget("Description\n On the given tab we are observing the shape of signal around "
                                        "spikes. which helps to analyse unit or multi-neural activities. you can "
                                        "choose several channels or an average of them by selecting average check box.")
        super().__init__(*args, self.view)

        self.view.set_plot_func(self.plot_clicked)

    @catch_exception
    def plot_clicked(self):
        marked_channels = self.view.channel_widget.marked_spike_channels
        if len(marked_channels) == 0:
            raise ValueError("At least one channel should be marked")

        if self._dialog:
            self._dialog.accept()
            self._dialog = None

        self.view.create_plot_window("Spike together", "icons/spike_together.png")
        self.mdi.addSubWindow(self.view.plot_window)

        if self.view.channel_widget.is_avg:
            spike_obj = self._create_spiketogether_module(marked_channels)
            plot_spikes_together(spike_obj.cutouts, spike_obj.labels, spike_obj.fs,
                                 spike_obj.component_number, spike_obj.pre, spike_obj.post, number_spikes=None,
                                 canvas=self.view.canvas, title=marked_channels, ax_idx=0)
        else:
            for i, ch in enumerate(marked_channels):
                spike_obj = self._create_spiketogether_module([ch])
                plot_spikes_together(spike_obj.cutouts, spike_obj.labels, spike_obj.fs,
                                     spike_obj.component_number, spike_obj.pre, spike_obj.post, number_spikes=None,
                                     canvas=self.view.canvas, title=ch, ax_idx=i)
        self.view.plot_window.show()
        self.view.plot_widget.mousePressEvent = lambda x: self.parameters_dock.setWidget(self.view)
        self.view.plot_window.closeEvent = lambda x: self._remove_me()
        self.view.canvas.mousePressEvent = lambda x: self.parameters_dock.setWidget(self.view)
        self.view.canvas.figure.tight_layout()

    def _create_spiketogether_module(self, marked_channels):
        return SpikeTogether(self.view.pre.text(), self.view.post.text(), self.view.component_number.text(),
                             self.view.dead_time.text(), self.view.threshold_from.text(), self.view.threshold_to.text(),
                             self.file.recordings[0].analog_streams[0], marked_channels, self.view.from_s.text(),
                             self.view.to_s.text(), self.view.high_pass.text(), self.view.low_pass.text())

    def _remove_me(self):
        del self.open_window_dict[self._key]
        self.parameters_dock.setWidget(get_default_widget())