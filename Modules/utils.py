from scipy.signal import butter, sosfilt
from McsPy import ureg, Q_
from functools import reduce
import numpy as np


def check_time_range(electrode_stream, sampling_frequency, from_in_s, to_in_s):
    signal_shape = electrode_stream.channel_data.shape[1]

    from_idx = max(0, int(from_in_s * sampling_frequency))
    from_idx = min(signal_shape, from_idx)
    if to_in_s is None:
        to_idx = signal_shape
    else:
        to_idx = min(signal_shape, int(to_in_s * sampling_frequency))
        to_idx = max(0, to_idx)
    if from_idx == to_idx:
        from_idx -= 1
    return from_idx, to_idx


def get_signal_time(electrode_stream, channels, sampling_frequency, from_in_s, to_in_s):
    from_idx, to_idx = check_time_range(electrode_stream, sampling_frequency, from_in_s, to_in_s)
    time = electrode_stream.get_channel_sample_timestamps(channels[0], from_idx, to_idx)
    signal_summed = reduce(lambda a, b: a+b, map(lambda ch: np.array(electrode_stream.get_channel_in_range(ch, from_idx, to_idx)), channels))
    signal_avg = signal_summed / len(channels)
    scale_factor_for_second = Q_(1, time[1]).to(ureg.s).magnitude
    time_in_sec = time[0] * scale_factor_for_second
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


def plot_signal(signal_in_uv, title, time_in_sec, canvas):

    axes = canvas.figure.get_axes()
    ax = axes[0]
    ax.clear()
    ax.plot(time_in_sec, signal_in_uv, linewidth=0.5)

    ax.set_xlabel('Time (%s)' % ureg.s)
    ax.set_ylabel('Voltage (%s)' % ureg.uV)
    ax.set_title(title)

    canvas.figure.tight_layout()
    canvas.draw()
