from scipy.signal import butter, sosfilt
from functools import reduce
import numpy as np


def convert_channel_label_to_id(electrode_stream, channel_label):
    channel_info = electrode_stream.channel_infos
    my_dict = {}
    for ch in channel_info:
        my_dict[int(channel_info.get(ch).info['Label'])] = int(ch)
    return my_dict.get(int(channel_label))


def get_signal_and_time(electrode_stream, channels, fs, from_idx, to_idx):
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


def calculate_threshold_based_on_signal(signal):
    noise_std= np.std(signal)
    noise_mad = np.median(np.absolute(signal))
    if noise_mad <= noise_std:
        return -5 * noise_mad
    else:
        return -5 * noise_std


def calculate_min_voltage_of_signal(signal):
    return np.min(signal)


def is_number(x):
    try:
        float(x)
        return True
    except ValueError:
        return None


def calculate_spikes(signal, threshold_from, threshold_to, dead_time_idx):
    last_idx = -dead_time_idx
    threshold_crossings = []
    for idx in range(len(signal)):
        if (idx > 0) and (signal[idx-1] > threshold_from) and (signal[idx] <= threshold_from) and \
                (signal[idx] >= threshold_to) and (idx - last_idx > dead_time_idx + 1):
            threshold_crossings.append(idx)
            last_idx = idx
    return np.array(threshold_crossings)

def calculate_bursts(spikes_in_s, max_start, max_end, min_between, min_duration, min_number_spike):
    spikes_in_s = np.array(spikes_in_s)
    all_burst = []
    i = 0
    while i < len(spikes_in_s)-1:
        if (spikes_in_s[i+1]-spikes_in_s[i]) <= max_start:
            burst_start_in_s = spikes_in_s[i]
            while (i < len(spikes_in_s)-1) and ((spikes_in_s[i+1]-spikes_in_s[i]) < max_end):
                i += 1
            burst_end_in_s = spikes_in_s[i]   
            all_burst.append([burst_start_in_s, burst_end_in_s])
            i+=1
        else:
            i+=1
    if not all_burst:
        return [], []

    merged_bursts=[]
    temp_burst = all_burst[0]
    for i in range(1, len(all_burst)):
        if (all_burst[i][0] - temp_burst[1]) < min_between:
            temp_burst[1] = all_burst[i][1]
        else:
            merged_bursts.append(temp_burst)
            temp_burst = all_burst[i]
    merged_bursts.append(temp_burst)

    bursts_starts = []
    bursts_ends = []
    for burst in merged_bursts:
        num_spike_in_burst = len(spikes_in_s[(spikes_in_s>=burst[0]) & (spikes_in_s<=burst[1])])
        if (((burst[1]-burst[0]) >= min_duration) and (num_spike_in_burst >= min_number_spike)):
            bursts_starts.append(burst[0])
            bursts_ends.append(burst[1])
    return bursts_starts, bursts_ends
