import matplotlib.backends.backend_qt5agg
import numpy
from McsPy import McsData
from matplotlib import pyplot as plt
from scipy.signal import butter, sosfilt
from functools import reduce
from typing import List
import numpy as np
from matplotlib.lines import Line2D
from sklearn.mixture import GaussianMixture
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler


def convert_channel_label_to_id(electrode_stream, channel_label: str) -> int:
    """
    convert_channel_label_to_id
    channel labels are the labels for particular electrode stream system
    for example in our key values, keys are the labels and values id's
                            {47: 0, 48: 1, 46: 2, 45: 3, 38: 4, 37: 5, 28: 6, 36: 7, 27: 8, 17: 9,
                            26: 10, 16: 11, 35: 12, 25: 13, 15: 14, 14: 15, 24: 16, 34: 17, 13: 18,
                            23: 19, 12: 20, 22: 21, 33: 22, 21: 23, 32: 24, 31: 25, 44: 26, 43: 27,
                            41: 28, 42: 29, 52: 30, 51: 31, 53: 32, 54: 33, 61: 34, 62: 35, 71: 36,
                            63: 37, 72: 38, 82: 39, 73: 40, 83: 41, 64: 42, 74: 43, 84: 44, 85: 45,
                            75: 46, 65: 47, 86: 48, 76: 49, 87: 50, 77: 51, 66: 52, 78: 53, 67: 54,
                            68: 55, 55: 56, 56: 57, 58: 58, 57: 59}

    Args:
            electrode_stream (McsPy.McsData.AnalogStream):  we need this to get the actual labels
                                                            and id's that this electrode stream has
            channel_label (str): the actual label of the id we are interested in

    Returns:
            corresponding channel id of the channel_label argument
    """
    channel_info = electrode_stream.channel_infos
    my_dict = {}
    for ch in channel_info:
        my_dict[int(channel_info.get(ch).info['Label'])] = int(ch)
    return my_dict.get(int(channel_label))


def get_signal(electrode_stream: McsData.AnalogStream, channels: List[int], from_idx: int,
               to_idx: int) -> numpy.ndarray:
    """
    get_signal uses Mcspy's method for getting signal in particular range and averaging if it's needed

    Args:
            electrode_stream (McsPy.McsData.AnalogStream): the main data object of the recording
            channels (list -> int): user's chosen channels to get signal
            from_idx (int): user's chosen start time translated into indexes, if None, we consider 0
            to_idx (int): user's chosen end time translated into indexes, if None, max length of recording list

    Returns:
            signal_avg (numpy.ndarray -> numpy.float64): the averaged signal in volts
                                                         (if multiple channels averaged, else signal itself)

    """
    signal_summed = reduce(lambda a, b: a + b,
                           map(lambda ch: np.array(electrode_stream.get_channel_in_range(ch, from_idx, to_idx)[0]),
                               channels))
    signal_avg = signal_summed / len(channels)
    return signal_avg


def filter_base_frequency(signal: numpy.ndarray, fs: int, high_pass: int, low_pass: int) -> numpy.ndarray:
    """
    filter_base_frequency filters signal with corresponding frequency filters, uses scipy butter library

    Args:
            signal (numpy.ndarray -> numpy.float64): the signal in volts
            fs (int): hertz, sampling frequency of the signal
            high_pass (int): hertz, everything lower than this frequency will be removed from signal
            low_pass (int): hertz, everything higher than this frequency will be removed from signal

    Returns:
            filtered (numpy.ndarray -> numpy.float64): the filtered signal in volts

    """
    butter_range = 2

    if (high_pass and high_pass >= fs / 2) or (low_pass and low_pass >= fs / 2):
        return signal * 0
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


def round_to_closest(value: float, time_stamp: float) -> float:
    """
    we have the recordings in every time_stamp seconds , so we need to round the user's values to those time_stamps

    example:
             if we recorded the signal in every 0.005 seconds, and user want's to plot signal from 0 to 0.009 second,
             we can't be able to split our signal in 0.009 second, because we don't have such steps,
             so we need to round the 0.009 to 0.01 and continue the process accordingly

    Args:
            value (float): second
            time_stamp (float): 1/fs , the step in which we have recorded signal

    Returns:
            value (float): rounded second

    """
    if value and value > 0:
        remainder = value % time_stamp
        value -= remainder
    return value


def _get_next_minimum(signal: numpy.ndarray, index: int, max_samples_to_search: int) -> float:
    """
    _get_next_minimum searches for next minimum value in the corresponding indexes

    Args:
            signal (numpy.ndarray -> numpy.float64): signal in volts
            index (int): the index, where from we need to start search
            max_samples_to_search(int): max number of values in which we need minimum

    Returns:
            index (float): the index of the found minimum value
    """
    search_end_idx = min(index + max_samples_to_search, signal.shape[0])
    min_idx = np.argmin(signal[index:search_end_idx])
    return index + min_idx


def _align_to_minimum(signal: numpy.ndarray, threshold_crossings: List[int], fs: int) \
        -> numpy.ndarray:
    """

    _align_to_minimum aligns the detected threshold crossings to minimum value in the search range to get spikes

    Args:
            signal (numpy.ndarray -> numpy.float64): signal in volts
            threshold_crossings (list -> int): indexes of crossed thresholds
            fs (int): hertz, sampling frequency of the signal

    Returns:
            aligned_spikes (numpy.ndarray -> numpy.int64): indexes of aligned spikes
    """
    search_range = 0.002
    search_end = int(search_range * fs)
    aligned_spikes = np.array([_get_next_minimum(signal, t, search_end) for t in threshold_crossings])
    return aligned_spikes


def get_signal_cutouts(signal: numpy.ndarray, fs: int, spikes_idx: numpy.ndarray,
                       pre: float, post: float) -> List:
    """
    get_signal_cutouts takes existing spikes, and cuts the signal around each of the spikes (pre-spike, spike-post)

    Args:
            signal (numpy.ndarray -> numpy.float64): signal in volts
            spikes_idx (numpy.ndarray -> numpy.int64): spike indexes in signals
            pre (float): seconds
            post (float): seconds
            fs (int): hertz, sampling frequency of the signal

    Returns:
            cutouts (list -> numpy.ndarray -> numpy.float64): signal parts arnd spikes, len of cutouts is len of spikes_idx
    """
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


def get_pca_labels(cutouts: List, n_components: int) -> numpy.ndarray:
    """
    get_pca_labels uses pca to calculate which cutouts are from the same neuron groups and which aren't

    Args:
            cutouts (list -> numpy.ndarray -> numpy.float64): cutouts made from signals around spikes
            n_components (int): this is the number of groups, if we think here are 3 neuron's spikes,
                                n_components should be 3

    Returns:
            predicted pca labels (numpy.ndarray -> numpy.int64): the len of this should be
                                                                 the len of spikes
    """
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


def get_spikes_with_labels(labels: numpy.ndarray, spikes: numpy.ndarray) -> List[tuple]:
    """
    we need this function to attribute the spikes to corresponding neurons and colors.

    Args:
            labels (numpy.ndarray -> numpy.int64): the len of this should be the len of spikes
            spikes (numpy.ndarray -> numpy.int64): calculated spikes

    Returns:
            spikes_with_labels (list -> tuple): color and the corresponding spike indices
    """
    unique = np.unique(np.array(labels))
    spikes_with_labels = []
    for i in unique:
        indices = [j for j, x in enumerate(labels) if x == i]
        spikes_with_labels.append((spikes[indices], plt.rcParams['axes.prop_cycle'].by_key()['color'][i]))
    return spikes_with_labels


def calculate_spikes(signal: numpy.ndarray, threshold_from: float, threshold_to: float, fs: int
                     , dead_time_idx: int) -> List[int]:
    """
    spikes are a representation of neural activity, for the calculation methodology,
    we take user's thresholds and dead_time_idx and move on the signal,
    while the value satisfies the thresholds, we skip the dead_time_idx and continue the searching process

    Args:
            signal (numpy.ndarray -> numpy.float64): signal in volts
            threshold_from (float): volts
            threshold_to (float): volts
            fs (int): hertz, sampling frequency of the signal
            dead_time_idx (int): the index quantity we need to skip after finding one spike

    Returns:
            threshold_crossings (list -> int): indexes of calculated spikes
    """
    if threshold_from > 0 and threshold_to > 0:
        threshold_from = threshold_from * (-1)
        threshold_to = threshold_to * (-1)
        signal = signal * (-1)

    last_idx = -dead_time_idx
    threshold_crossings = []
    for idx in range(len(signal)):
        if (idx > 0) and (signal[idx - 1] > threshold_from) and \
                (signal[idx] <= threshold_from) and (idx - last_idx > dead_time_idx + 1):
            threshold_crossings.append(idx)
            last_idx = idx
    threshold_crossings = _align_to_minimum(signal, threshold_crossings, fs)
    threshold_crossings = np.array(list(filter(lambda x: signal[x] >= threshold_to, threshold_crossings)))
    return np.array(threshold_crossings)


def calculate_stimulus(signal: numpy.ndarray, threshold: float, dead_time_idx: int) -> List[int]:
    """
    stimulus are artificially made, and calculating them is necessary because
    unfortunately in our recordings, we don't have the information about the stimulus.
    we take user's thresholds and dead_time_idx and move on the signal, while the value
    satisfies the thresholds, we skip the dead_time_idx and continue the searching process

    Args:
            signal (numpy.ndarray -> numpy.float64): signal in volts
            threshold (float): volts
            dead_time_idx (int): the index quantity we need to skip after finding one stimulus

    Returns:
            threshold_crossings (list -> int): indexes of calculated stimulus
    """
    threshold_crossings = np.diff((signal <= threshold)).nonzero()[0]
    if len(threshold_crossings) == 0:
        return np.array([])

    distance_sufficient = np.insert(np.diff(threshold_crossings) >= dead_time_idx, 0, True)
    last_stimulus_index = threshold_crossings[-1]
    for i in range(1, len(distance_sufficient)):
        if distance_sufficient[i]:
            distance_sufficient[i - 1] = True

    while not np.all(distance_sufficient):
        threshold_crossings = threshold_crossings[distance_sufficient]
        distance_sufficient = np.insert(np.diff(threshold_crossings) >= dead_time_idx, 0, True)
        for i in range(1, len(distance_sufficient)):
            if distance_sufficient[i]:
                distance_sufficient[i - 1] = True

    if len(threshold_crossings) % 2 == 1:
        threshold_crossings = np.insert(threshold_crossings, len(threshold_crossings), last_stimulus_index)
    return threshold_crossings


def calculate_bursts(spikes_in_s: List[numpy.float64], max_start: float
                     , max_end: float, min_between: float, min_duration: float, min_number_spike: int):
    """
    TODO

    Args:
            spikes_in_s (list -> numpy.float64): calculated spikes in second
            max_start (float):
            max_end (float):
            min_between (float):
            min_duration (float):
            min_number_spike (int):
    Returns:
            bursts_starts ():
            bursts_starts ():
    """
    spikes_in_s = np.array(spikes_in_s)
    all_burst = []
    i = 0
    while i < len(spikes_in_s) - 1:
        if (spikes_in_s[i + 1] - spikes_in_s[i]) <= max_start:
            burst_start_in_s = spikes_in_s[i]
            while (i < len(spikes_in_s) - 1) and ((spikes_in_s[i + 1] - spikes_in_s[i]) < max_end):
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
        if ((burst[1] - burst[0]) >= min_duration) and (num_spike_in_burst >= min_number_spike):
            bursts_starts.append(burst[0])
            bursts_ends.append(burst[1])
    print("bursts_starts", type(bursts_starts), bursts_starts)
    print("bursts_ends", type(bursts_ends), bursts_ends)
    return bursts_starts, bursts_ends


def calculate_threshold_based_on_signal(signal: numpy.ndarray) -> float:
    """
    if user didn't specify the threshold, we calculate it based on the signal values (standard deviation)

        Args:
                signal (numpy.ndarray -> numpy.float64): signal in volts

        Returns:
                threshold (float): signal's threshold calculated based on standard deviation and median
    """
    noise_std = np.std(signal)
    noise_mad = np.median(np.absolute(signal))
    if noise_mad <= noise_std:
        return -5 * noise_mad
    else:
        return -5 * noise_std


def calculate_min_voltage_of_signal(signal: numpy.ndarray) -> numpy.float64:
    """
    This function calculates the minimum value of the numpy array

    Args:
        signal (numpy.ndarray -> numpy.float64): signal in volts

    Returns:
        minimum value of signal
    """
    return np.min(signal)


def calculate_bins(spikes_in_range, from_s: float, bin_width: int):
    """


        Args:
                spikes_in_range ():
                from_s ():
                bin_width ():


        Returns:
                spike_len_in_bins ():
    """
    spike_len_in_bins = []
    if not len(spikes_in_range):
        return [0]

    spikes_last_index = len(spikes_in_range) - 1
    bin_start_second = from_s
    counter = 0
    idx = 0

    while True:
        if idx > spikes_last_index:
            spike_len_in_bins.append(counter)
            break
        if spikes_in_range[idx] < (bin_start_second + bin_width):
            counter += 1
            idx += 1
        else:
            spike_len_in_bins.append(counter)
            bin_start_second += bin_width
            counter = 0

    spike_len_in_bins = list(map(lambda x: int(x / bin_width), spike_len_in_bins))
    return spike_len_in_bins


def plot_signal(signal: numpy.ndarray, time_in_sec: numpy.ndarray
                , canvas: matplotlib.backends.backend_qt5agg.FigureCanvasQTAgg
                , title: str, x_label: str, y_label: str, ax_idx=0) -> None:
    """
    this function only plots the signal in the canvas

        Args:
                signal (numpy.ndarray -> numpy.float64): signal in volts
                time_in_sec (numpy.ndarray -> numpy.float64): list of seconds
                canvas (matplotlib.backends.backend_qt5agg.FigureCanvasQTAgg): canvas to draw on
                title (str): title of the plot
                x_label (str): x label of the plot
                y_label (str): y label of the plot
                ax_idx (int): the index in which axes it should be drawn
    """

    axes = canvas.figure.get_axes()
    ax = axes[ax_idx]
    ax.clear()
    signal_in_uv = signal * 1000000
    ax.plot(time_in_sec, signal_in_uv, linewidth=0.5)

    ax.set_title(title)
    canvas.figure.text(0.5, 0.01, x_label, ha='center')
    canvas.figure.text(0.01, 0.5, y_label, va='center', rotation='vertical')

    canvas.draw()


def plot_signal_with_spikes(signal: numpy.ndarray,
                            time_in_sec: numpy.ndarray,
                            canvas: matplotlib.backends.backend_qt5agg.FigureCanvasQTAgg,
                            title: str, x_label: str, y_label: str,
                            indices_colors_for_spikes: List[tuple], ax_idx: int = 0,
                            indices_colors_for_bursts: List[tuple] = []) -> None:
    """
    this function plots both spikes and signal together in the one canvas window

        Args:
                signal (numpy.ndarray -> numpy.float64): signal in volts
                time_in_sec (numpy.ndarray -> numpy.float64): list of seconds
                canvas (matplotlib.backends.backend_qt5agg.FigureCanvasQTAgg): canvas to draw on
                title (str): title of the plot
                x_label (str): x label of the plot
                y_label (str): y label of the plot
                indices_colors_for_spikes (list -> tuple): each tuple contains color in hex and the indices list
                indices_colors_for_bursts (list -> tuple): each tuple contains color in hex and the indices list
                ax_idx (int): the index in which axes it should be drawn
    """
    signal_in_uv = signal * 1000000

    axes = canvas.figure.get_axes()
    ax = axes[ax_idx]
    ax.clear()
    ax.plot(time_in_sec, signal_in_uv, linewidth=0.5, color="darkmagenta")
    burst_legend = Line2D([], [], color='darkorange', marker='|', linestyle='None',
                          markersize=10, markeredgewidth=2.5, label='Burst')
    spike_legend = Line2D([], [], color='green', marker='o', linestyle='None',
                          markersize=5, markeredgewidth=1, label='Spike')
    ax.legend(handles=[spike_legend, burst_legend])

    for indices, colors in indices_colors_for_spikes:
        indices_ = [ind / 25000 + time_in_sec[0] for ind in indices]
        ax.plot(indices_, signal_in_uv[indices], 'ro', ms=2, color=colors, zorder=1)
    if len(indices_colors_for_bursts):
        for indices in indices_colors_for_bursts:
            burst_starts_list = indices[0][0]
            burst_ends_list = indices[0][1]
            for i in range(len(burst_starts_list)):
                temp_burst_start = burst_starts_list[i] / 25000 + time_in_sec[0]
                temp_burst_end = burst_ends_list[i] / 25000 + time_in_sec[0]
                ax.axvspan(temp_burst_start, temp_burst_end, facecolor='0.2', alpha=0.5, color=indices[1])

    canvas.figure.tight_layout()
    canvas.draw()
    ax.set_title(title)
    canvas.figure.text(0.5, 0.01, x_label, ha='center')
    canvas.figure.text(0.01, 0.5, y_label, va='center', rotation='vertical')


def plot_bins(spike_in_bins, bin_ranges, bin_width: int
              , canvas: matplotlib.backends.backend_qt5agg.FigureCanvasQTAgg
              , title: str, x_label: str, y_label: str, ax_idx: int = 0, **kwargs) -> None:
    """
    what to do with kwargs TODO

    """
    x = bin_ranges
    y = [value for value in spike_in_bins]

    axes = canvas.figure.get_axes()
    ax = axes[ax_idx]
    ax.clear()

    ax.bar(x, y, width=bin_width, align='edge', alpha=0.4, facecolor='blue', edgecolor='red', linewidth=2, **kwargs)
    ax.grid(color='#95a5a6', linestyle='--', linewidth=1, axis='y', alpha=0.7)

    ax.set_title(title)
    canvas.figure.text(0.5, 0.01, x_label, ha='center')
    canvas.figure.text(0.01, 0.5, y_label, va='center', rotation='vertical')
    canvas.draw()


def _plot_each_spike(ax, cutouts: numpy.ndarray, fs: int, pre: float, post: float, n: int = 100
                     , color: str = 'k', title: str = "") -> None:
    """
    this function plots each spike cutout

        Args:
                ax (canvas.figure.axis): the axis where the current cutout should be drawn
                cutouts (numpy.ndarray -> numpy.ndarray -> numpy.float64):
                                                cutouted signal from spikes (pre-spike, spike-post)
                fs (int): hertz, sampling frequency of the signal
                pre (float): seconds
                post (float): seconds
                n (int): size of cutout
                color (str): color code of current cutout
                title (str): title of the plot
    """
    if n is None:
        n = cutouts.shape[0]
    else:
        n = int(n)
    n = min(n, cutouts.shape[0])

    pre = int(pre * fs) / fs
    post = int(post * fs) / fs
    time_in_us = np.arange(-pre * 1000, post * 1000, 1e3 / fs)

    for i in range(n):
        ax.plot(time_in_us, cutouts[i] * 1e6, color, linewidth=1, alpha=0.3)

    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Voltage (uV)')
    ax.set_title(title)


def plot_spikes_together(cutouts: numpy.ndarray, labels: numpy.ndarray
                         , fs: int, n_components: int, pre: float, post: float, number_spikes: int
                         , canvas: matplotlib.backends.backend_qt5agg.FigureCanvasQTAgg
                         , title: str, ax_idx: int) -> None:
    """
    this function plots spike cutouts in the canvas

        Args:
                cutouts (numpy.ndarray -> numpy.ndarray -> numpy.float64): cutouted signal from spikes (pre-spike, spike-post)
                labels ('numpy.ndarray -> 'numpy.int64): labels of different neurons , length of spikes
                n_components (int): number of different neurons
                number_spikes (int): number of spikes to draw
                pre (float): seconds
                post (float): seconds
                fs (int): hertz, sampling frequency of the signal
                canvas (matplotlib.backends.backend_qt5agg.FigureCanvasQTAgg): canvas to draw on
                title (str): title of the plot
                ax_idx (int): the index in which axes it should be drawn
    """
    axes = canvas.figure.get_axes()
    ax = axes[ax_idx]
    ax.clear()
    labels = np.array(labels)
    if len(cutouts) < 1:
        ax.set_title('No Spike')
        canvas.draw()
        return

    for i in range(int(n_components)):
        idx = labels == i
        color = plt.rcParams['axes.prop_cycle'].by_key()['color'][i]
        _plot_each_spike(ax, cutouts[idx, :], fs, pre, post, n=number_spikes, color=color, title=title)
    canvas.draw()


def plot_stimulus(stimulus: List[int], canvas: matplotlib.backends.backend_qt5agg.FigureCanvasQTAgg
                  , ax_idx: int = 0) -> None:
    """
    this function plots lines to show stimulus in canvas, in particular window using matplotlib axvline function

        Args:
                stimulus (list -> int): indexes of stimulus
                canvas (matplotlib.backends.backend_qt5agg.FigureCanvasQTAgg): canvas to draw on
                ax_idx (int): the index in which axes it should be drawn
    """
    axes = canvas.figure.get_axes()
    ax = axes[ax_idx]

    for s in stimulus:
        ax.axvline(s, alpha=0.7, color='lime')

    canvas.draw()


def filter_stimulus(stimulus: numpy.ndarray, useless_stimulus: List[tuple], from_s: float, fs: int) \
        -> List[numpy.int64]:
    """
    we need this function to clear stimulus which are in the useless_stimulus chosen by the user

        Args:
                stimulus (numpy.ndarray -> numpy.int64): indexes of stimulus
                useless_stimulus (list -> tuple): each item is from and to indicates seconds.
                from_s (float): second
                fs (int): hertz, sampling frequency of the signal


        Returns:
                stimulus (list -> numpy.int64): indexes of filtered stimulus
    """
    for i in range(0, len(useless_stimulus)):
        stimulus = [st for st in stimulus if not (useless_stimulus[i][0] < (st / fs + from_s) < useless_stimulus[i][1])]
    return stimulus
