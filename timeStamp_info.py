import numpy as np
import pandas as pd
import math
from sklearn.mixture import GaussianMixture
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

import gc
import os
from McsPy import McsData
from McsPy import ureg, Q_
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from scipy.fft import fft
from scipy.signal import butter, sosfilt

# helper functions
DETECT_CROSSINGS_TYPE = "Slow"
def _check_time_range(analog_stream, sampling_frequency, from_in_s, to_in_s):
    signal_shape = analog_stream.channel_data.shape[1]

    from_idx = max(0, int(from_in_s * sampling_frequency))
    from_idx = min(signal_shape, from_idx)
    if to_in_s is None:
        to_idx = signal_shape
    else:
        to_idx = min(signal_shape, int(to_in_s * sampling_frequency))
        to_idx = max(0, to_idx)
    if from_idx==to_idx:
        from_idx-=1
    return from_idx, to_idx

def _get_specific_channel_signal(analog_stream, channel_id, from_in_s, to_in_s, high_pass, low_pass):
    signal_in_uV, time_in_sec = _get_signal_time(analog_stream, channel_id, from_in_s, to_in_s)
    fs = int(analog_stream.channel_infos[channel_id].sampling_frequency.magnitude)
    signal_in_uV = _filter_base_freqeuncy(signal_in_uV, fs, high_pass, low_pass)
    return signal_in_uV

def _get_signal_cutouts(signal, fs, spikes_idx, pre, post):
    cutouts = []
    pre_idx = int(pre * fs)
    post_idx = int(post * fs)
    if pre_idx > 0 and post_idx > 0:
        for index in spikes_idx:
            if index-pre_idx >= 0 and index+post_idx <= signal.shape[0]:
                cutout = signal[(index-pre_idx):(index+post_idx)]
                cutouts.append(cutout)

        if (len(cutouts)>0) :
            return np.stack(cutouts)
    return cutouts

def _drop_extra_spike(spks, fs, pre, post, signal_idx):
    first_idx = spks[0]
    last_idx = spks[-1]
    pre_idx = int(pre*fs)
    post_idx = int(post*fs)

    if first_idx-pre_idx < 0 and last_idx+post_idx > signal_idx:
        spks = spks[1:-1]
    elif first_idx-pre_idx < 0:  
        spks = spks[1:]
    elif last_idx+post_idx > signal_idx:
        spks = spks[:-1]
    return spks

def _plot_each_spike(ax, cutouts, fs, pre, post, n=100, color='k'):
    if n is None:
        n = cutouts.shape[0]
    else:
        n = int(n)
    n = min(n, cutouts.shape[0])

    pre = int(pre * fs)/fs
    post = int(post * fs)/fs
    time_in_us = np.arange(-pre*1000, post*1000, 1e3/fs)
    
    for i in range(n):
        ax.plot(time_in_us, cutouts[i,]*1e6, color, linewidth=1, alpha=0.3)
        
    ax.set_xlabel('Time (%s)' % ureg.ms)
    ax.set_ylabel('Voltage (%s)' % ureg.uV)
    ax.set_title('Spike together')

def _get_next_minimum(signal, index, max_samples_to_search):
    search_end_idx = min(index + max_samples_to_search, signal.shape[0])
    min_idx = np.argmin(signal[index:search_end_idx])
    return index + min_idx

def _align_to_minimum(signal, fs, threshold_crossings, search_range):
    search_end = int(search_range*fs)
    aligned_spikes = np.array([_get_next_minimum(signal, t, search_end) for t in threshold_crossings])
    return aligned_spikes

def _filter_base_freqeuncy(signal_in_uV, fs, High_pass, Low_pass):    
    butter_range = 2

    if (High_pass and High_pass >= fs/2) or (Low_pass and Low_pass >= fs/2):
        return signal_in_uV*0
    if High_pass and Low_pass:
        sos = butter(N = butter_range, Wn = [High_pass, Low_pass], fs=fs, btype='band', output = 'sos')
    elif High_pass:
      sos = butter(N = butter_range, Wn = High_pass, btype='hp', fs=fs, output='sos')
    elif Low_pass:
      sos = butter(N = butter_range, Wn = Low_pass, btype='lp', fs=fs, output='sos')
    else:
      return signal_in_uV
    filtered = sosfilt(sos, signal_in_uV)
    return filtered

def _get_proper_threshold (signal, threshold_from, threshold_to, is_spike) :
    if not threshold_from:
        if is_spike: 
            noise_std= np.std(signal)
            noise_mad = np.median(np.absolute(signal))
            if noise_mad <= noise_std:
                threshold_from = -5 * noise_mad
            else:
                 threshold_from = -5 * noise_std
        else: 
            threshold_from=-100/1000000       
    if not threshold_to:
        threshold_to = np.min(signal)
    return threshold_from, threshold_to

def _get_pca_labels(cutouts, n_components):
    if n_components>=len(cutouts):
        n_components = 1
    pca = PCA()
    pca.n_components = int(2)
    scaler = StandardScaler()
    scaled_cutouts = scaler.fit_transform(abs(cutouts))
    scaled_cutouts *= 2

    transformed = pca.fit_transform(scaled_cutouts)
    gmm = GaussianMixture(n_components=int(n_components), n_init=10)
    return gmm.fit_predict(transformed)

def _get_signal_time(analog_stream, channel_id, from_in_s, to_in_s):
    channel_info = analog_stream.channel_infos[channel_id]
    sampling_frequency = channel_info.sampling_frequency.magnitude  
    from_idx ,to_idx = _check_time_range(analog_stream,sampling_frequency,from_in_s,to_in_s)  # get start and end index    
    time = analog_stream.get_channel_sample_timestamps(channel_id, from_idx, to_idx)
    signal = analog_stream.get_channel_in_range(channel_id, from_idx, to_idx)
    scale_factor_for_second = Q_(1,time[1]).to(ureg.s).magnitude
    time_in_sec = time[0] * scale_factor_for_second
    scale_factor_for_uV = Q_(1,signal[1]).to(ureg.uV).magnitude
    signal_in_uV = signal[0] * scale_factor_for_uV
    return signal_in_uV, time_in_sec

def _detect_threshold_crossings_spikes(signal, fs, threshold_from, threshold_to, dead_time):
    if not threshold_to:
      threshold_to = np.min(signal)

    dead_time_idx = dead_time * fs
    last_idx = -dead_time_idx
    threshold_crossings = []
    for idx in range(len(signal)):
        if idx > 0 and signal[idx-1] > threshold_from and signal[idx] <= threshold_from and idx - last_idx > dead_time_idx + 1:
            threshold_crossings.append(idx)
            last_idx = idx
    return np.array(threshold_crossings)

def _detect_threshold_crossings_spikes_fast(signal, fs, threshold, threshold_to, dead_time):
    dead_time_idx = dead_time * fs
    threshold_crossings = np.diff((signal <= threshold).astype(int) > 0).nonzero()[0]
    distance_sufficient = np.insert(np.diff(threshold_crossings) >= dead_time_idx, 0, True)
    while not np.all(distance_sufficient):
        # repeatedly remove all threshold crossings that violate the dead_time
        threshold_crossings = threshold_crossings[distance_sufficient]
        distance_sufficient = np.insert(np.diff(threshold_crossings) >= dead_time_idx, 0, True)
    return np.array(threshold_crossings)

def _get_spike_info(signal, fs, threshold_from, threshold_to, dead_time):
    if DETECT_CROSSINGS_TYPE=="Fast":
        crossings = _detect_threshold_crossings_spikes_fast(signal, fs, threshold_from, threshold_to, dead_time)
    else:
        crossings = _detect_threshold_crossings_spikes(signal, fs, threshold_from, threshold_to, dead_time)

    spks = _align_to_minimum(signal, fs, crossings, 0.002) # search range 2 ms
    return spks

def _detect_threshold_crossings_stimulus(signal, fs, threshold, dead_time):
    dead_time_idx = dead_time * fs
    threshold_crossings = np.diff((signal <= threshold)).nonzero()[0]
    if len(threshold_crossings)==0:
        return np.array([])

    distance_sufficient = np.insert(np.diff(threshold_crossings) >= dead_time_idx, 0, True)
    last_stimulus_index = threshold_crossings[-1]
    
    for i in range(1,len(distance_sufficient)):
      if distance_sufficient[i]:
        distance_sufficient[i-1] = True

    while not np.all(distance_sufficient):
        threshold_crossings = threshold_crossings[distance_sufficient]
        distance_sufficient = np.insert(np.diff(threshold_crossings) >= dead_time_idx, 0, True)
        for i in range (1,len(distance_sufficient)):
          if distance_sufficient[i]:
            distance_sufficient[i-1] = True
    
    if len(threshold_crossings)%2 == 1:
        threshold_crossings = np.insert(threshold_crossings,len(threshold_crossings),last_stimulus_index)
    return threshold_crossings

def _count_spike_in_bins(spike_in_s, bin_width, from_in_s):
    temp_bin = bin_width
    spike_len_in_bins = []
    if not from_in_s:
        from_in_s = 0
    spike_idx = 0
    count_spike = 0
    while spike_idx < len(spike_in_s):
        if (spike_in_s[spike_idx]-from_in_s) < temp_bin:
            count_spike += 1
            spike_idx += 1
        else:
            spike_len_in_bins.append(count_spike)
            count_spike = 0
            temp_bin += bin_width

    if count_spike != 0:
        spike_len_in_bins.append(count_spike)
    spike_len_in_bins = list(map(lambda x: int(x/bin_width), spike_len_in_bins))
    return spike_len_in_bins

def _get_channel_ID(electrode_stream, channel_label):
    if channel_label=="all":
        return "all"
    channel_info = electrode_stream.channel_infos   
    
    my_dict = {}
    for ch in channel_info:
      my_dict[int(channel_info.get(ch).info['Label'])]=int(ch)
    return my_dict.get(channel_label)

def _get_burst(spikes_in_s, max_start, max_end, min_between, min_duration, min_number_spike):
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

def _signal_average_around_stimulus(signal, stimulus_df, channel, pre, post, fs):
    if len(stimulus_df)==0:
        return pd.DataFrame(columns=["avg_stim_voltage"])

    pre_idx = int(pre * fs)
    post_idx = int(post * fs)
    stimulus_df = stimulus_df.astype('int32')
    temp = [0]*(pre_idx+post_idx)
    waveform_df=pd.DataFrame(temp,columns=["avg_stim_voltage"])
    for i in range(0,len(stimulus_df)) :
        index1 = stimulus_df["start"+str(channel)][i]
        index2 = stimulus_df["end"+str(channel)][i]
        if index1-pre_idx >= 0 and index2+post_idx <= signal.shape[0]:
            oneWaveform = np.concatenate((signal[(index1-pre_idx):index1],signal[index2:(index2+post_idx)]),axis=None)
            waveform_df["avg_stim_voltage"]+=oneWaveform
    return waveform_df/(len(stimulus_df))*1000000

def _save_stimulus_with_avg(file_save_path, signal, channel_id, from_in_s, to_in_s, stimulus_threshold, fs, pre, post, dead_time):
    stimulus_in_second_df = pd.DataFrame()
    threshold_from, _ = _get_proper_threshold(signal, stimulus_threshold, None, False)
    thresholds = _detect_threshold_crossings_stimulus(signal, fs, threshold_from, dead_time)/fs
    stimulus_in_second_df["start"+str(channel_id)] = [thresholds[i] for i in range(0,len(thresholds),2)]
    stimulus_in_second_df["end"+str(channel_id)] = [thresholds[i] for i in range(1,len(thresholds),2)]
    stimulus_in_second_df["stimulus_time"+str(channel_id)] = (stimulus_in_second_df["end"+str(channel_id)] - stimulus_in_second_df["start"+str(channel_id)])
    stimulus_in_second_df["stimulus_number"+str(channel_id)] = np.ceil(stimulus_in_second_df["stimulus_time"+str(channel_id)] / dead_time)

    df_avg_stimul = (_signal_average_around_stimulus(signal, stimulus_in_second_df*fs, channel_id, pre, post, fs))/1000000
    stimulus_in_second_df["start"+str(channel_id)] += from_in_s
    stimulus_in_second_df["end"+str(channel_id)] += from_in_s
    stimulus_in_second_df.to_csv(file_save_path+str(channel_id)+".csv", index = False)
    df_avg_stimul.to_csv(file_save_path+str(channel_id)+"_avg_stimulus.csv", index=False)

def _clear_plot(canvas, *, subplot_num):
    axes = canvas.figure.get_axes()
    ax = axes[subplot_num]
    ax.clear()

def _plot_signal(signal_in_uV, title, time_in_sec, canvas, suplot_num):

    axes = canvas.figure.get_axes()
    ax = axes[suplot_num]
    ax.clear()
    ax.plot(time_in_sec, signal_in_uV, linewidth=0.5)

    ax.set_xlabel('Time (%s)' % ureg.s)
    ax.set_ylabel('Voltage (%s)' % ureg.uV)
    ax.set_title(title)

    canvas.figure.tight_layout()
    canvas.draw()
    gc.collect()

def _plot_all_spikes_together(signal_in_uV, fs, n_components, pre, post, number_spikes, canvas, suplot_num, spks):  

    cutouts = _get_signal_cutouts(signal_in_uV, fs, spks, pre, post)

    axes = canvas.figure.get_axes()
    ax = axes[suplot_num]
    ax.clear()
    if (len(cutouts) < 2):
        ax.set_title('No Spike')
        canvas.figure.tight_layout()
        return []
    labels = _get_pca_labels(cutouts, n_components)
    for i in range(int(n_components)):
        idx = labels == i
        color = plt.rcParams['axes.prop_cycle'].by_key()['color'][i]
        _plot_each_spike(ax, cutouts[idx,:], fs, pre, post, n=number_spikes, color=color)
    canvas.figure.tight_layout()
    canvas.draw()
    gc.collect()
    return labels

def _plot_stimulus_average(signal_in_uV, channel_label, fs, thresholds, dead_time, stimulus_threshold, pre, post, canvas, suplot_num):

    signal = signal_in_uV/1000000

    stimulus_df = pd.DataFrame()
    stimulus_df["start"+str(channel_label)] = [int(thresholds[i]) for i in range(0,len(thresholds)) if i%2==0]
    stimulus_df["end"+str(channel_label)] = [int(thresholds[i]) for i in range(0,len(thresholds)) if i%2==1]

    df_to_draw = _signal_average_around_stimulus(signal, stimulus_df, channel_label, pre, post, fs)
    x = np.linspace(-pre, post, len(df_to_draw))
    xx = [0,0]
    yx=[df_to_draw.max(),df_to_draw.min()]
    axes = canvas.figure.get_axes()
    ax = axes[suplot_num]
    ax.clear()
    ax.plot(x, df_to_draw, linewidth=2)
    ax.plot(xx, yx, linewidth=2, color='lime')
    
    ax.set_xlabel('Time (%s)' % ureg.s)
    ax.set_ylabel('Voltage (%s)' % ureg.uV)
    canvas.figure.tight_layout()
    canvas.draw()
    gc.collect()

def _plot_signal_with_spikes_or_stimulus(signal_in_uV, time_in_sec, channel_id, channel_id_converted, fs, canvas, suplot_num, is_spike, from_in_s, to_in_s, threshold_from, threshold_to, spks, dead_time,
                                        max_start=None, max_end=None, min_between=None, min_duration=None, min_number_spike=None, stimulus=[], labels=[]):
    
    signal = signal_in_uV/1000000
    if not len(spks):
        spikes_voltage = []
    else:    
        spikes_voltage = signal[spks]*1000000

    spikes_in_range = spks / fs
    spikes_in_range = np.array(spikes_in_range)
    spikes_in_range += from_in_s
    axes = canvas.figure.get_axes()
    ax = axes[suplot_num]
    ax.clear()
    ax.plot(time_in_sec, signal_in_uV, linewidth=0.5, color = "darkmagenta")
    if is_spike: # just for painting 
        ax.plot(spikes_in_range, spikes_voltage, 'ro', ms=2 , zorder=1)
        if len(spikes_in_range>=2):
            unique = np.unique(np.array(labels))
            for i in unique:
                indices = [j for j, x in enumerate(labels) if x == i]
                ax.plot(spikes_in_range[indices], spikes_voltage[indices], 'ro', ms=2 , zorder=1, color=plt.rcParams['axes.prop_cycle'].by_key()['color'][i])
        burst_legend = Line2D([], [], color='darkorange', marker='|', linestyle='None', markersize=10, markeredgewidth=2.5, label='Burst')
        stimulus_legend = Line2D([], [], color='lime', marker='|', linestyle='None', markersize=10, markeredgewidth=2.5, label='Stimulus')
        spike_legend = Line2D([], [], color='red', marker='o', linestyle='None', markersize=5, markeredgewidth=1, label='Spike')
        ax.legend(handles =[spike_legend, burst_legend, stimulus_legend])
    else:
        ax.scatter(spikes_in_range, [threshold_from*1e6]*spikes_in_range.shape[0], color = 'lime', marker='o', s = 8, zorder=2, alpha=0.7)
        stimulus_legend = Line2D([], [], color='lime', marker='o', linestyle='None', markersize=5, markeredgewidth=1, label='Stimulus')
        ax.legend(handles =[stimulus_legend])

    for stimul in stimulus:
        if not to_in_s: 
            to_in_s = time_in_sec[len(time_in_sec)-1]

        if stimul>=from_in_s and stimul<=to_in_s:
            ax.axvspan(stimul, stimul+5*40/1000000, facecolor='0.2', alpha=0.7, color='lime')

    if (not (None in [max_start, max_end, min_between, min_duration, min_number_spike])):
        spikes_in_second = spks/fs

        bursts_starts, bursts_ends = _get_burst(spikes_in_second, max_start, max_end, min_between, min_duration, min_number_spike)
        bursts_df = pd.DataFrame({"burst_start":bursts_starts, "burst_end":bursts_ends})
        bursts_df += from_in_s

        for idx in range(bursts_df.shape[0]):
            temp_burst_start = bursts_df.iloc[idx].burst_start
            temp_burst_end = bursts_df.iloc[idx].burst_end
            ax.axvspan(temp_burst_start, temp_burst_end, facecolor='0.2', alpha=0.7, color='darkorange')
    
    ax.set_xlabel('Time (%s)' % ureg.s)
    ax.set_ylabel('Voltage (%s)' % ureg.uV)
    ax.set_title('Channel %s' % str(channel_id))
    canvas.figure.tight_layout()
    canvas.draw()
    gc.collect()
    return spikes_in_range

def _plot_signal_frequencies(signal_in_uV, time_in_sec, canvas, suplot_num):
    
    X = fft(signal_in_uV)
    X[(len(time_in_sec)//2+1):]=0

    axes = canvas.figure.get_axes()
    ax = axes[suplot_num]
    ax.clear()
    ax.plot(abs(X[1:]), linewidth=0.5, color = "darkorange")
    
    ax.set_xlabel('Frequency (Hz)')
    canvas.figure.tight_layout()
    canvas.draw()
    gc.collect()

def _plot_bins(channel_id, spikes_in_second, fs, canvas, from_in_s, to_in_s, from_idx, to_idx, bin_width, subplot_num, stimulus, time_in_sec):
    df = pd.DataFrame()
    bin_ranges = [bin_width*i for i in list(range(int(np.ceil((to_idx-from_idx+1)/fs/bin_width))))]
    df["bin_ranges"] = np.array(bin_ranges)+ from_in_s
    spike_in_bins = _count_spike_in_bins(spikes_in_second, bin_width, from_in_s)
    df["spike_num_"] = pd.Series(spike_in_bins)
    x = df.iloc[:,0]
    y = [0 if math.isnan(value) else int(value) for value in df.iloc[:,1]]

    axes = canvas.figure.get_axes()
    ax = axes[subplot_num]
    ax.clear()
    pps = ax.bar(x, y, width = bin_width, align='edge', alpha=0.4, facecolor='blue', edgecolor='red', linewidth=2)
    ax.grid(color='#95a5a6', linestyle='--', linewidth=1, axis='y', alpha=0.7)

    for stimul in stimulus:
        if not to_in_s:
            to_in_s = time_in_sec[len(time_in_sec)-1]

        if stimul>=from_in_s and stimul<=to_in_s:
            ax.axvspan(stimul, stimul+5*40/1000000, facecolor='0.2', alpha=0.7, color='lime')

    ax.set_ylabel('Bin Frequency')
    ax.set_xlabel('Bin time step (second)')
    canvas.figure.tight_layout()
    canvas.draw()
    gc.collect()

def _calculate_average_signal(electrode_stream, channel_id, from_in_s, to_in_s):
    signal_in_uV = []
    channel_id_converted = []  # channel_ID which is used in methods, not ID which is visualised in app
    time_in_sec = []
    for ch in channel_id:
        ch = _get_channel_ID(electrode_stream, int(ch))
        channel_id_converted.append(ch)
        signal_in_uV_temp, time_in_sec = _get_signal_time(electrode_stream, ch, from_in_s, to_in_s) 
        if len(signal_in_uV)==0:
            signal_in_uV = signal_in_uV_temp
        else:
            signal_in_uV += signal_in_uV_temp
    signal_in_uV /= len(channel_id)
    return signal_in_uV, channel_id_converted, time_in_sec

def _get_spikes_dataframe_to_extract(electrode_stream, channel_ids, from_in_s, signal_if_avg, to_in_s, threshold_from, threshold_to, high_pass, low_pass, dead_time, 
                                bin_width, max_start, max_end, min_between, min_duration, min_number_spike, stimulus, pre, post, n_components, reduce_num):
                                
    spikes_df = pd.DataFrame()
    bins_df = pd.DataFrame()
    _, time_in_sec = _get_signal_time(electrode_stream, channel_ids[0], from_in_s, to_in_s) 
    fs = int(electrode_stream.channel_infos[0].sampling_frequency.magnitude)
    fs_reduced = fs
    from_idx, to_idx = _check_time_range(electrode_stream, fs, from_in_s, to_in_s)
    from_idx_reduced = from_idx
    to_idx_reduced = to_idx

    if bin_width:
        bin_ranges = [bin_width*i for i in list(range(int(np.ceil((to_idx-from_idx+1)/fs/bin_width))))]
        bins_df["bin_ranges"] = np.array(bin_ranges)+ from_in_s

    for channel_id in channel_ids:
        if len(signal_if_avg)>0:
            channel_label = "avg"
            signal_if_avg /= 1000000
            if reduce_num and reduce_num > 0:
                signal_if_avg, fs_reduced = _reduce_signal(signal_if_avg, fs, int(reduce_num))
                time_in_sec = np.arange(0, len(signal_if_avg))/fs_reduced
            signal_if_avg = _filter_base_freqeuncy(signal_if_avg, fs_reduced, high_pass, low_pass)
            spikes_df["time"] = time_in_sec+from_in_s
            spikes_df["signal_avg"] = signal_if_avg  # This part is for average signal, to save the voltage of average signal
            threshold_from, threshold_to = _get_proper_threshold(signal_if_avg, threshold_from, threshold_to, True)
            spks = _get_spike_info(signal_if_avg, fs_reduced, threshold_from, threshold_to, dead_time)
            spks = np.array(list(filter(lambda x: signal_if_avg[x]>=threshold_to, spks)))
            spks = _drop_extra_spike(spks, fs_reduced, pre, post, signal_if_avg.shape[0])
            cutouts = _get_signal_cutouts(signal_if_avg, fs_reduced, spks, pre, post)
        else:
            channel_label = electrode_stream.channel_infos.get(channel_id).info['Label']            
            signal = electrode_stream.get_channel_in_range(channel_id, from_idx, to_idx)[0]
            if reduce_num and reduce_num > 0:
                signal, fs_reduced = _reduce_signal(signal, fs, int(reduce_num))
                time_in_sec = np.arange(0, len(signal))/fs_reduced
            signal = _filter_base_freqeuncy(signal, fs_reduced, high_pass, low_pass)
            spikes_df["time"] = time_in_sec+from_in_s
            threshold_from, threshold_to = _get_proper_threshold(signal, threshold_from, threshold_to, True)       
            spks = _get_spike_info(signal, fs_reduced, threshold_from, threshold_to, dead_time)
            spikes_df["signal_"+str(channel_label)] = signal
            spks = np.array(list(filter(lambda x: signal[x]>=threshold_to, spks)))
            spks = _drop_extra_spike(spks, fs_reduced, pre, post, signal.shape[0])
            cutouts = _get_signal_cutouts(signal, fs_reduced, spks, pre, post)

        if len(spks)<1:
            spikes_df["spikes"+str(channel_label)] = np.zeros(len(spikes_df))
            spikes_df["bursts"+str(channel_label)] = np.zeros(len(spikes_df))
            continue

        to_be_spikes = np.zeros(len(spikes_df))
        if len(cutouts) >=2:
            labels = _get_pca_labels(cutouts, n_components)
            labels = labels + 1
        else:
            labels = np.ones(len(spks))
        to_be_spikes[spks] = labels
        spikes_df["spikes"+str(channel_label)] = to_be_spikes
        spikes_in_second = spks/fs_reduced
        spikes_in_second += from_in_s

        if bin_width:
            spike_in_bins = _count_spike_in_bins(spikes_in_second, bin_width, from_in_s)
            bins_df["spike_num_"+str(channel_label)] = pd.Series(spike_in_bins)

        if (not (None in [max_start, max_end, min_between, min_duration, min_number_spike])):
            spikes_in_second -= from_in_s
            bursts_starts, _ = _get_burst(spikes_in_second, max_start, max_end, min_between, min_duration, min_number_spike)
            bursts_starts = (np.array(bursts_starts)*fs_reduced).astype(int)
            to_be_bursts = np.zeros(len(spikes_df))
            to_be_bursts[bursts_starts] = 1
            spikes_df["bursts"+str(channel_label)] = to_be_bursts
        else:
            spikes_df["bursts"+str(channel_label)] = np.zeros(len(spikes_df))

    if reduce_num and reduce_num > 0:
        from_idx_reduced = from_idx / reduce_num
        to_idx_reduced = to_idx / reduce_num

    if len(stimulus) > 0 :
        stimulus = (np.array(stimulus)*fs_reduced).astype(int)
        stimulus_in_range = stimulus[(stimulus >= from_idx_reduced) & (stimulus <= to_idx_reduced)]
        stimulus_in_range -= int(from_idx_reduced)
        to_be_stimulus = np.zeros(len(spikes_df))
        to_be_stimulus[stimulus_in_range] = 1
        spikes_df["stimulus"] = to_be_stimulus
    else:
        spikes_df["stimulus"] = np.zeros(len(spikes_df))
    
    return spikes_df, bins_df

def _reduce_signal(signal, fs, reduce_num):
    lst = list(signal)
    pad = reduce_num - (len(lst) % reduce_num)
    lst = lst + [0] * pad

    l = np.array(lst)
    l = l.reshape(len(lst) // reduce_num, -1)
    l = l.sum(axis=1)
    l.reshape(1, -1)
    l = l / reduce_num

    return l, fs / reduce_num



# main functions

def plot_tab1(electrode_stream, channel_id, from_in_s, to_in_s, canvas, high_pass, low_pass, check_boxes):
    signal_in_uV , channel_id_converted, time_in_sec = _calculate_average_signal(electrode_stream, [channel_id], from_in_s, to_in_s)
    fs = int(electrode_stream.channel_infos[0].sampling_frequency.magnitude)
    signal_in_uV_filtered = _filter_base_freqeuncy(signal_in_uV, fs, high_pass, low_pass)
    _plot_signal(signal_in_uV_filtered, "Original Signal", time_in_sec, canvas, 0)

    if check_boxes[1] and int(check_boxes[1]) > 0:
        signal_in_uV, fs = _reduce_signal(signal_in_uV, fs, int(check_boxes[1]))
        signal_in_uV = _filter_base_freqeuncy(signal_in_uV, fs, high_pass, low_pass)
        time_in_sec = np.arange(0, len(signal_in_uV))/fs
        _plot_signal(signal_in_uV, "After Reducing", time_in_sec, canvas, 1)
    else:
        _clear_plot(canvas, subplot_num=1)

    return 0,""

def plot_tab2(electrode_stream, channel_id, from_in_s, to_in_s, high_pass, low_pass, threshold_from, threshold_to, dead_time, check_boxes, pre, post, canvas,
                comp_number, spike_number, stimulus, max_start, max_end, min_between, min_duration, min_number_spike, bin_width, reduce_num, detecting_type):

    global DETECT_CROSSINGS_TYPE
    DETECT_CROSSINGS_TYPE = detecting_type
    signal_in_uV , channel_id_converted, time_in_sec = _calculate_average_signal(electrode_stream, channel_id, from_in_s, to_in_s)
    fs = int(electrode_stream.channel_infos[0].sampling_frequency.magnitude)
    from_idx, to_idx = _check_time_range(electrode_stream, fs, from_in_s, to_in_s) 

    if reduce_num and reduce_num > 0:
        signal_in_uV, fs = _reduce_signal(signal_in_uV, fs, int(reduce_num))
        time_in_sec = np.arange(0, len(signal_in_uV))/fs
        if from_in_s:
            time_in_sec += from_in_s
        from_idx /= reduce_num
        to_idx /= reduce_num
    signal_in_uV = _filter_base_freqeuncy(signal_in_uV, fs, high_pass, low_pass)  
    signal = signal_in_uV/1000000 
    threshold_from, threshold_to = _get_proper_threshold(signal, threshold_from, threshold_to, True)
    spks = _get_spike_info(signal, fs, threshold_from, threshold_to, dead_time)
    spks = _drop_extra_spike(spks, fs, pre, post, to_idx)
    spks = np.array(list(filter(lambda x: signal[x]>=threshold_to, spks))) 

    if check_boxes[0].isChecked():
        labels = _plot_all_spikes_together(signal_in_uV, fs, comp_number, pre, post, spike_number, canvas, 0, spks)
    else:
        _clear_plot(canvas, subplot_num=0)
        labels = []
    
    if check_boxes[1].isChecked():
        spikes_in_range = _plot_signal_with_spikes_or_stimulus(signal_in_uV, time_in_sec, channel_id, channel_id_converted, fs, canvas, 1, True, from_in_s, to_in_s,
                                            threshold_from, threshold_to, spks, dead_time, max_start, max_end, min_between, min_duration, min_number_spike, stimulus, labels)
    else:
        _clear_plot(canvas, subplot_num=1)

    if check_boxes[2].isChecked() and bin_width:
        _plot_bins(channel_id, spikes_in_range, fs, canvas, from_in_s, to_in_s, from_idx, to_idx, bin_width, 2, stimulus, time_in_sec)

    else:
        _clear_plot(canvas, subplot_num=2)
    
    return 0, ""

def plot_tab3(electrode_stream, channel_id, from_in_s, to_in_s, high_pass, low_pass, threshold_from, threshold_to, dead_time, check_boxes, pre, post, canvas, reduce_num):

    signal_in_uV , channel_id_converted, time_in_sec = _calculate_average_signal(electrode_stream, [channel_id], from_in_s, to_in_s)
    fs = int(electrode_stream.channel_infos[0].sampling_frequency.magnitude)
    from_idx, to_idx = _check_time_range(electrode_stream, fs, from_in_s, to_in_s)
    if reduce_num and reduce_num > 0:
        signal_in_uV, fs = _reduce_signal(signal_in_uV, fs, int(reduce_num))
        time_in_sec = np.arange(0, len(signal_in_uV))/fs
        if from_in_s:
            time_in_sec += from_in_s
    signal_in_uV = _filter_base_freqeuncy(signal_in_uV, fs, high_pass, low_pass)  
    signal = signal_in_uV/1000000
    threshold_from, threshold_to = _get_proper_threshold(signal, threshold_from, threshold_to, True)
    thresholds = _detect_threshold_crossings_stimulus(signal, fs, threshold_from, dead_time)
    if len(thresholds):
        thresholds = np.array(list(filter(lambda x: signal[x]>=threshold_to, thresholds))) 

    if check_boxes[0].isChecked():
        _plot_stimulus_average(signal_in_uV, channel_id, fs, thresholds, dead_time, threshold_from, pre, post, canvas, 0)
    else:
        _clear_plot(canvas, subplot_num=0)

    if check_boxes[1].isChecked():
        stimulus = _plot_signal_with_spikes_or_stimulus(signal_in_uV, time_in_sec, channel_id, channel_id_converted, fs, canvas, 1, False, from_in_s, to_in_s, threshold_from, threshold_to, thresholds, dead_time)
    else:
        stimulus = []
        _clear_plot(canvas, subplot_num=1)

    if check_boxes[2].isChecked():
        _plot_signal_frequencies(signal_in_uV, time_in_sec, canvas, 2)
    else:
        _clear_plot(canvas, subplot_num=2)

    return 0, stimulus


def extract_waveform(analog_stream, file_save_path, channel_id, from_in_s, to_in_s, high_pass, low_pass, reduce_num):   
    _channel_info = analog_stream.channel_infos[0]
    sampling_frequency = _channel_info.sampling_frequency.magnitude
    from_idx ,to_idx = _check_time_range(analog_stream,sampling_frequency,from_in_s,to_in_s)  # get start and end index
    time = analog_stream.get_channel_sample_timestamps(0, from_idx, to_idx)  # get the timestamps for each sample 
    scale_factor_for_second = Q_(1,time[1]).to(ureg.s).magnitude  # scale time to seconds
    time_in_sec = time[0] * scale_factor_for_second
    fs = int(analog_stream.channel_infos[0].sampling_frequency.magnitude)
    fs_reduced = fs
    df=pd.DataFrame()
    if (channel_id==None):
        for channel in analog_stream.channel_infos:     
            channel_label = analog_stream.channel_infos.get(channel).info['Label']
            signal = (_get_specific_channel_signal(analog_stream,channel,from_in_s,to_in_s,high_pass,low_pass))/1000000
            if reduce_num and reduce_num > 0:
                signal, fs_reduced = _reduce_signal(signal, fs, int(reduce_num))
            df["signal for "+str(channel_label)] = signal
        time_in_sec = np.arange(0, len(signal))/fs_reduced
        df["time_in_sec"] = time_in_sec
    else:
        channel_label = channel_id
        channel_id = _get_channel_ID(analog_stream, channel_id)
        signal = (_get_specific_channel_signal(analog_stream,channel_id,from_in_s,to_in_s,high_pass,low_pass))/1000000
        if reduce_num and reduce_num > 0:
            signal, fs = _reduce_signal(signal, fs, int(reduce_num))
            time_in_sec = np.arange(0, len(signal))/fs
        df["signal for "+str(channel_label)] = signal
        df["time_in_sec"] = time_in_sec
    
    df.to_csv(file_save_path+".csv", index=False)
    gc.collect()

def extract_stimulus(analog_stream, file_save_path, channel_id, from_in_s, to_in_s, stimulus_threshold, dead_time, pre, post, high_pass, low_pass, reduce_num):
    _channel_info = analog_stream.channel_infos[0]
    fs = _channel_info.sampling_frequency.magnitude
    fs_reduced = fs
    from_idx, to_idx = _check_time_range(analog_stream, fs, from_in_s, to_in_s)
    if (channel_id==None):
        for channel in analog_stream.channel_infos:
            channel_id = analog_stream.channel_infos.get(channel).info['Label']
            signal = analog_stream.get_channel_in_range(channel, from_idx, to_idx)[0]
            if reduce_num and reduce_num > 0:
                signal, fs_reduced = _reduce_signal(signal, fs, int(reduce_num))
            signal = _filter_base_freqeuncy(signal, fs, high_pass, low_pass)
            _save_stimulus_with_avg(file_save_path, signal, channel_id, from_in_s, to_in_s, stimulus_threshold, fs_reduced, pre, post, dead_time)
    else:
        channel = _get_channel_ID(analog_stream, channel_id)
        signal = analog_stream.get_channel_in_range(channel, from_idx, to_idx)[0]
        if reduce_num and reduce_num > 0:
            signal, fs_reduced = _reduce_signal(signal, fs, int(reduce_num))
        signal = _filter_base_freqeuncy(signal, fs_reduced, high_pass, low_pass)
        _save_stimulus_with_avg(file_save_path, signal, channel_id, from_in_s, to_in_s, stimulus_threshold, fs_reduced, pre, post, dead_time)
    gc.collect()

def extract_spike(file_path, analog_stream, file_save_path, channel_id, from_in_s, to_in_s, threshold_from, threshold_to, high_pass, low_pass, dead_time, bin_width,
                max_start, max_end, min_between, min_duration, min_number_spike, stimulus, pre, post, n_cpmponents, reduce_num):

    if len(channel_id) == 1 :
        if channel_id[0] == "all":
            channel_ids = [key for key, value in analog_stream.channel_infos.items()]
            spikes_df,bins_df = _get_spikes_dataframe_to_extract(analog_stream, channel_ids, from_in_s, [], to_in_s, threshold_from, threshold_to, high_pass, low_pass, dead_time,
                                                                    bin_width, max_start, max_end, min_between, min_duration, min_number_spike, stimulus, pre, post, n_cpmponents, reduce_num)
        else:
            channel_id_converted = [_get_channel_ID(analog_stream, int(channel_id[0]))]
            spikes_df,bins_df = _get_spikes_dataframe_to_extract(analog_stream, channel_id_converted, from_in_s, [], to_in_s, threshold_from, threshold_to, high_pass, low_pass, dead_time,
                                                                        bin_width, max_start, max_end, min_between, min_duration, min_number_spike, stimulus, pre, post, n_cpmponents, reduce_num)
    else:
        signal_if_avg,_,_ =  _calculate_average_signal(analog_stream, channel_id, from_in_s, to_in_s)
        channel_ids = [0]
        spikes_df, bins_df = _get_spikes_dataframe_to_extract(analog_stream, channel_ids, from_in_s, signal_if_avg, to_in_s, threshold_from, threshold_to, high_pass, low_pass, dead_time,
                                                                    bin_width, max_start, max_end, min_between, min_duration, min_number_spike, stimulus, pre, post, n_cpmponents, reduce_num)
    
    # save part of DataFrames
    if spikes_df.size > 0 :
        spikes_df["channel"] = "-".join([str(value) for value in channel_id])
        spikes_df["stimulus_type"] = file_save_path.split("_")[-1]
        spikes_df["file_name"] = os.path.basename(file_path).split(".")[0]
        spikes_df.to_csv(file_save_path+"_spikes.csv", index = False)
    if bins_df.size > 0 :
        bins_df.to_csv(file_save_path+"_bins.csv", index = False)

    gc.collect()

