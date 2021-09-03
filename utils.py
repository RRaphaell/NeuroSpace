from McsPy import McsData
from Widgets.WaveformWidget import WaveformWidget


def path_valid(file_name):
    try:
        file = McsData.RawData(file_name)
    except:
        file = None
    return file


def partial_dock_widget(dock, widget):
    dock = dock
    widget = widget

    def inner():
        dock.setWidget(widget)
    return inner


def get_default_widget():
    waveform_widget = WaveformWidget(None, None)
    waveform_widget.setDisabled(True)
    return waveform_widget
