import os
import pandas as pd
from McsPy import McsData
from Widgets.WaveformWidget import WaveformWidget


def path_valid(file_name):
    """
    path_valid function both validates the file_name and also reads it

    Args:
            file_name (str) - should be related to h5 file
    Returns:
            file ('McsPy.McsData.RawData'> / None): it has different type of returns
                                                    depends on whether path exists or not
    """
    try:
        file = McsData.RawData(file_name)
    except:
        file = None
    return file


def get_default_widget():
    """
    get_default_widget function makes a default waveform widget object
    which is displayed on left side of the app, immediately

    Returns:
            waveform_widget (WaveformWidget): disabled, default waveform widget object
    """
    waveform_widget = WaveformWidget("", None, None)
    waveform_widget.setDisabled(True)
    return waveform_widget


def merge_files(dir_name: str) -> None:
    """
    merge_files combines same type of files together,
    it goes through the input directory, reads all files,
    merges them in one dataframe and saves the combined file
    as a "combined.csv" file in the "dir_name" directory.

    Args:
             dir_name (str) - should be related to the directory,
                        where files which we want to merge, exist

    Returns:
             None, just creates a file in directory
    """
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
