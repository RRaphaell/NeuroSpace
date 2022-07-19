import pandas as pd
from Controllers.Controller import Controller
from Controllers.utils import catch_exception
from Modules.Waveform import Waveform
from Widgets.WaveformWidget import WaveformWidget
from Modules.utils import plot_signal


class WaveformController(Controller):
    """
    WaveformController class is for UI and module relationship while displaying the waveform widget
    On the given widget we are observing the behavior of the selected signals.

    Note that, Arguments are documented in parent class
    """
    def __init__(self, *args):
        self.view = WaveformWidget("Description\n On the given tab we are observing the behavior of the selected "
                                   "signals. You can analyze several channels or an average of them by selecting "
                                   "average check box.", title="Waveform")
        super().__init__(*args, self.view)

        self.view.set_plot_func(self.plot_clicked)
        self.view.set_extract_func(self.extract_clicked)

    @catch_exception
    def plot_clicked(self) -> None:
        """
        This function firstly makes the waveform module object, preprocesses signal and then uses
        waveform plot function from utils to plot the desired signal.
        """
        marked_channels = self.view.channel_widget.marked_spike_channels
        if len(marked_channels) == 0:
            raise ValueError("At least one channel should be marked")

        if self._dialog:
            self._dialog.accept()
            self._dialog = None

        self.view.create_plot_window("Waveform", "icons/waveform.png")
        self.mdi.addSubWindow(self.view.plot_window)

        if self.view.channel_widget.is_avg:
            waveform = self._create_waveform(marked_channels)
            filtered_signal = waveform.signal
            plot_signal(filtered_signal, waveform.time, self.view.canvas,
                        marked_channels, "Time (seconds)", "Signal (uV)", ax_idx=0)
        else:
            for i, ch in enumerate(marked_channels):
                waveform = self._create_waveform([ch])
                filtered_signal = waveform.signal
                plot_signal(filtered_signal, waveform.time, self.view.canvas,
                            ch, "Time (seconds)", "Signal (uV)", ax_idx=i)

        self.view.plot_window.show()
        self.view.plot_widget.mousePressEvent = lambda x: self.parameters_dock.setWidget(self.view)
        self.view.plot_window.closeEvent = lambda x: self._remove_me()
        self.view.canvas.mousePressEvent = lambda x: self.parameters_dock.setWidget(self.view)
        self.view.canvas.figure.tight_layout()

    @catch_exception
    def extract_clicked(self):
        """
        This function firstly makes the waveform module object, preprocesses signal and then uses
        extracts that desired signal into the user's desired input path
        """
        path = self.view.get_path_for_save()
        if path:
            marked_channels = self.view.channel_widget.marked_spike_channels
            if len(marked_channels) == 0:
                raise ValueError("At least one channel should be marked")

            if self.view.channel_widget.is_avg:
                waveform_dataframe = pd.DataFrame()
                waveform = self._create_waveform(marked_channels)
                waveform_dataframe["time"] = waveform.time
                waveform_dataframe[f"Signal_{marked_channels}"] = waveform.signal
                waveform_dataframe.to_csv(path + ".csv", index=False)

            else:
                waveform_dataframe = pd.DataFrame()
                for i, ch in enumerate(marked_channels):
                    waveform = self._create_waveform([ch])
                    if i == 0:
                        waveform_dataframe["time"] = waveform.time
                    waveform_dataframe[f"signal_{ch}"] = waveform.signal
                waveform_dataframe.to_csv(path + ".csv", index=False)

            self.popup_handler.info_popup("Success", "Data Created successfully")

    def _create_waveform(self, channels: list) -> Waveform:
        """
        Creates waveform class object
        """
        return Waveform(self.file.recordings[0].analog_streams[0], channels, self.view.from_s.text(),
                        self.view.to_s.text(), self.view.high_pass.text(), self.view.low_pass.text())
