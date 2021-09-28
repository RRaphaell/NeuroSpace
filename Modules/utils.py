from matplotlib import pyplot as plt
from scipy.signal import butter, sosfilt
from functools import reduce
import numpy as np
from matplotlib.lines import Line2D
from sklearn.mixture import GaussianMixture
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler


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


def plot_signal(signal, time_in_sec, canvas, title, x_label, y_label, ax_idx=0):

    axes = canvas.figure.get_axes()
    ax = axes[ax_idx]
    ax.clear()
    signal_in_uv = signal*1000000
    ax.plot(time_in_sec, signal_in_uv, linewidth=0.5)

    ax.set_title(title)
    canvas.figure.text(0.5, 0.01, x_label, ha='center')
    canvas.figure.text(0.01, 0.5, y_label, va='center', rotation='vertical')

    canvas.draw()


def plot_signal_with_spikes(signal, time_in_sec, canvas, labels, title, x_label, y_label, spikes_indexes,
                            ax_idx=0, indices_colors_for_bursts=[]):
    signal_in_uv = signal * 1000000
    # if not len(spikes_indexes):
    #     spikes_voltage = []
    # else:
    #     spikes_voltage = signal[spikes_indexes]*1000000

    axes = canvas.figure.get_axes()
    ax = axes[ax_idx]
    ax.clear()
    ax.plot(time_in_sec, signal_in_uv, linewidth=0.5, color="darkmagenta")
    burst_legend = Line2D([], [], color='darkorange', marker='|', linestyle='None',
                          markersize=10, markeredgewidth=2.5, label='Burst')
    spike_legend = Line2D([], [], color='green', marker='o', linestyle='None',
                          markersize=5, markeredgewidth=1, label='Spike')
    ax.legend(handles=[spike_legend, burst_legend])

    indices_colors_for_spikes = get_spikes_with_labels(labels, spikes_indexes)
    for indices, colors in indices_colors_for_spikes:
        indices_ = [ind / 25000 for ind in indices]
        ax.plot(indices_, signal_in_uv[indices], 'ro', ms=2, color=colors)
    if len(indices_colors_for_bursts):
        for indices in indices_colors_for_bursts:
            burst_starts_list = indices[0][0]
            burst_ends_list = indices[0][1]
            for i in range(len(burst_starts_list)):
                temp_burst_start = burst_starts_list[i] / 25000
                temp_burst_end = burst_ends_list[i] / 25000
                ax.axvspan(temp_burst_start, temp_burst_end, facecolor='0.2', alpha=0.5, color=indices[1])

    canvas.figure.tight_layout()
    canvas.draw()
    ax.set_title(title)
    canvas.figure.text(0.5, 0.01, x_label, ha='center')
    canvas.figure.text(0.01, 0.5, y_label, va='center', rotation='vertical')


def plot_bins(spike_in_bins, bin_ranges, bin_width, canvas, title, x_label, y_label, ax_idx=0):
    x = bin_ranges
    y = [int(value) for value in spike_in_bins]

    axes = canvas.figure.get_axes()
    ax = axes[ax_idx]
    ax.clear()

    ax.bar(x, y, width=bin_width, align='edge', alpha=0.4, facecolor='blue', edgecolor='red', linewidth=2)
    ax.grid(color='#95a5a6', linestyle='--', linewidth=1, axis='y', alpha=0.7)

    # for stimul in stimulus:
    #     if not to_in_s:
    #         to_in_s = time_in_sec[len(time_in_sec)-1]

    #     if stimul>=from_in_s and stimul<=to_in_s:
    #         ax.axvspan(stimul, stimul+5*40/1000000, facecolor='0.2', alpha=0.7, color='lime')

    ax.set_title(title)
    canvas.figure.text(0.5, 0.01, x_label, ha='center')
    canvas.figure.text(0.01, 0.5, y_label, va='center', rotation='vertical')
    canvas.draw()


def _plot_each_spike(ax, cutouts, fs, pre, post, n=100, color='k', title=""):
    if n is None:
        n = cutouts.shape[0]
    else:
        n = int(n)
    n = min(n, cutouts.shape[0])

    pre = int(pre * fs) / fs
    post = int(post * fs) / fs
    time_in_us = np.arange(-pre * 1000, post * 1000, 1e3 / fs)

    for i in range(n):
        ax.plot(time_in_us, cutouts[i]*1e6, color, linewidth=1, alpha=0.3)

    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Voltage (uV)')
    ax.set_title(title)


def plot_spikes_together(cutouts, labels, fs, n_components, pre, post, number_spikes, canvas, title, ax_idx):
    axes = canvas.figure.get_axes()
    ax = axes[ax_idx]
    ax.clear()

    if len(cutouts) < 2:
        ax.set_title('No Spike')
        canvas.draw()
        return

    for i in range(int(n_components)):
        idx = labels == i
        color = plt.rcParams['axes.prop_cycle'].by_key()['color'][i]
        _plot_each_spike(ax, cutouts[idx, :], fs, pre, post, n=number_spikes, color=color, title=title)
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
    noise_std = np.std(signal)
    noise_mad = np.median(np.absolute(signal))
    if noise_mad <= noise_std:
        return -5 * noise_mad
    else:
        return -5 * noise_std


def calculate_min_voltage_of_signal(signal):
    return np.min(signal)


def calculate_spikes(signal, threshold_from, threshold_to, fs, dead_time_idx):
    last_idx = -dead_time_idx
    threshold_crossings = []
    for idx in range(len(signal)):
        if (idx > 0) and (signal[idx-1] > threshold_from) and (signal[idx] <= threshold_from) and \
                (signal[idx] >= threshold_to) and (idx - last_idx > dead_time_idx + 1):
            threshold_crossings.append(idx)
            last_idx = idx
    threshold_crossings = _align_to_minimum(signal, threshold_crossings, fs)
    return np.array(threshold_crossings)


def _get_next_minimum(signal, index, max_samples_to_search):
    search_end_idx = min(index + max_samples_to_search, signal.shape[0])
    min_idx = np.argmin(signal[index:search_end_idx])
    return index + min_idx


def _align_to_minimum(signal, threshold_crossings, fs):
    search_range = 0.002
    search_end = int(search_range*fs)
    aligned_spikes = np.array([_get_next_minimum(signal, t, search_end) for t in threshold_crossings])
    return aligned_spikes


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
            i += 1
        else:
            i += 1
    if not all_burst:
        return [], []

    merged_bursts = []
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
        num_spike_in_burst = len(spikes_in_s[(spikes_in_s >= burst[0]) & (spikes_in_s <= burst[1])])
        if ((burst[1]-burst[0]) >= min_duration) and (num_spike_in_burst >= min_number_spike):
            bursts_starts.append(burst[0])
            bursts_ends.append(burst[1])
    return bursts_starts, bursts_ends


def get_signal_cutouts(signal, fs, spikes_idx, pre, post):
    cutouts = []
    pre_idx = int(pre * fs)
    post_idx = int(post * fs)
    if pre_idx > 0 and post_idx > 0:
        for index in spikes_idx:
            if index - pre_idx >= 0 and index + post_idx <= signal.shape[0]:
                cutout = signal[(index - pre_idx):(index + post_idx)]
                cutouts.append(cutout)

        if len(cutouts) > 0:
            return np.stack(cutouts)
    return cutouts


def get_pca_labels(cutouts, n_components):
    if n_components >= len(cutouts):
        n_components = 1
    pca = PCA()
    pca.n_components = int(2)
    scaler = StandardScaler()
    scaled_cutouts = scaler.fit_transform(abs(cutouts))
    scaled_cutouts *= 2

    transformed = pca.fit_transform(scaled_cutouts)
    gmm = GaussianMixture(n_components=int(n_components), n_init=10)
    return gmm.fit_predict(transformed)


def get_spikes_with_labels(labels, spikes):
    unique = np.unique(np.array(labels))
    spikes_with_labels = []
    for i in unique:
        indices = [j for j, x in enumerate(labels) if x == i]
        spikes_with_labels.append((spikes[indices], plt.rcParams['axes.prop_cycle'].by_key()['color'][i]))
    return spikes_with_labels
