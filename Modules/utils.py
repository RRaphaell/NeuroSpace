from scipy.signal import butter, sosfilt
from McsPy import ureg


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
