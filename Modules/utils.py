from scipy.signal import butter, sosfilt
from functools import reduce
import numpy as np
import pandas as pd


def get_signal_and_time(electrode_stream, channels, fs, from_idx, to_idx):
    signal_summed = reduce(lambda a, b: a+b, map(lambda ch: np.array(electrode_stream.get_channel_in_range(ch, from_idx, to_idx)), channels))
    signal_avg = signal_summed / len(channels)
    time_in_sec = np.array(range(from_idx,to_idx+1))/fs
    return signal_avg[0], time_in_sec



def filter_base_frequency(signal, fs, high_pass, low_pass):
    butter_range = 2

    if (high_pass and high_pass >= fs / 2) or (low_pass and low_pass >= fs / 2):
        return signal*0
    if high_pass and low_pass:
        sos = butter(N=butter_range, Wn=[high_pass, low_pass], fs=fs, btype='band', output='sos')
    elif high_pass:
        sos = butter(N=butter_range, Wn=high_pass, btype='hp', fs=fs, output='sos')
    elif low_pass:
        sos = butter(N=butter_range, Wn=low_pass, btype='lp', fs=fs, output='sos')
    else:
        return signal

    filtered = sosfilt(sos, signal)
    return filtered


def plot_signal(signal, title, time_in_sec, canvas):

    axes = canvas.figure.get_axes()
    ax = axes[0]
    ax.clear()
    signal_in_uv = signal*1000000
    ax.plot(time_in_sec, signal_in_uv, linewidth=0.5)

    ax.set_xlabel('Time in s')
    ax.set_ylabel('Voltage in uV')
    ax.set_title(title)

    canvas.figure.tight_layout()
    canvas.draw()

def extract_signal(signal, time, file_save_path):
    waveform_dataFrame = pd.DataFrame()
    waveform_dataFrame["Time"] = time
    waveform_dataFrame["Signal in v"] = signal
    waveform_dataFrame.to_csv(file_save_path+".csv", index=False)
