import os
import pandas as pd
from McsPy import McsData
from Widgets.WaveformWidget import WaveformWidget


def path_valid(file_name):
    try:
        file = McsData.RawData(file_name)
    except:
        file = None
    return file


def get_default_widget():
    waveform_widget = WaveformWidget("", None, None)
    waveform_widget.setDisabled(True)
    return waveform_widget


def merge_files(dir_name):
    if dir_name:
        if os.path.exists(os.path.join(dir_name, "combined.csv")):
            os.remove(os.path.join(dir_name, "combined.csv"))
        files = os.listdir(dir_name)
        if not len(files):
            return

        combined = pd.DataFrame()
        for file in files:
            temp_df = pd.read_csv(os.path.join(dir_name, file))
            combined = pd.concat([combined, temp_df])

        combined.to_csv(os.path.join(dir_name, "combined.csv"), index=False)
