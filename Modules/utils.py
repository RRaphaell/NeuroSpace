from scipy.signal import butter, sosfilt
from functools import reduce
import numpy as np
import pandas as pd


def get_channel_id(electrode_stream, channel_label):
    channel_info = electrode_stream.channel_infos
    my_dict = {}
    for ch in channel_info:
        my_dict[int(channel_info.get(ch).info['Label'])] = int(ch)
    return my_dict.get(channel_label)


def get_signal_and_time(electrode_stream, channels, fs, from_idx, to_idx):
    channels = list(map(lambda ch: get_channel_id(electrode_stream, ch), channels))
    signal_summed = reduce(lambda a, b: a+b, map(lambda ch: np.array(electrode_stream.get_channel_in_range(ch, from_idx, to_idx)[0]), channels))
    signal_avg = signal_summed / len(channels)
    time_in_sec = np.array(range(from_idx, to_idx+1))/fs
    return signal_avg, time_in_sec


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


def plot_signal(signal, time_in_sec, canvas, x_label, y_label, ax_idx=0):

    axes = canvas.figure.get_axes()
    ax = axes[ax_idx]
    ax.clear()
    signal_in_uv = signal*1000000
    ax.plot(time_in_sec, signal_in_uv, linewidth=0.5)

    canvas.figure.text(0.5, 0.01, x_label, ha='center')
    canvas.figure.text(0.01, 0.5, y_label, va='center', rotation='vertical')

    canvas.draw()


def round_to_closest(value, time_stamp):
    if value and value > 0:
        remainder = value % time_stamp
        if remainder > time_stamp / 2:
            value += time_stamp - remainder
        else:
            value -= remainder
    return value
