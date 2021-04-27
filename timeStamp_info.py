import os
import numpy as np
import pandas as pd
from sklearn.mixture import GaussianMixture
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

import McsPy
import McsPy.McsData
from McsPy import ureg, Q_
import matplotlib.pyplot as plt
from scipy.fft import ifft, fft

# helper functions

def _check_time_range(analog_stream, sampling_frequency, from_in_s, to_in_s):
    from_idx = max(0, int(from_in_s * sampling_frequency))
    if to_in_s is None:
        to_idx = analog_stream.channel_data.shape[1]
    else:
        to_idx = min(analog_stream.channel_data.shape[1], int(to_in_s * sampling_frequency))
    return from_idx, to_idx

def _get_specific_channel_signal(analog_stream, channel_id, from_idx, to_idx):
    signal = analog_stream.get_channel_in_range(channel_id, from_idx, to_idx) # get the signal 
    signal_in_uV = signal[0] * Q_(1,signal[1]).to(ureg.uV).magnitude # scale signal to µV
    return signal_in_uV

def _get_signal_cutouts(signal, fs, spikes_idx, pre, post):
    cutouts = []
    pre_idx = int(pre * fs)
    post_idx = int(post * fs)
    for index in spikes_idx:
        if index-pre_idx >= 0 and index+post_idx <= signal.shape[0]:
            cutout = signal[(index-pre_idx):(index+post_idx)]
            cutouts.append(cutout)
    if (len(cutouts)>0) :
        return np.stack(cutouts)
    return cutouts

def _plot_each_spike(ax, cutouts, fs, pre, post, n=100, color='k'):

    if n is None:
        n = cutouts.shape[0]
    else:
        n = int(n)
    n = min(n, cutouts.shape[0])
    time_in_us = np.arange(-pre*1000, post*1000, 1e3/fs)
    
    for i in range(n):
        ax.plot(time_in_us, cutouts[i,]*1e6, color, linewidth=1, alpha=0.3)
        
        ax.set_xlabel('Time (%s)' % ureg.ms)
        ax.set_ylabel('Voltage (%s)' % ureg.uV)
        ax.set_title('Cutouts')

def _detect_threshold_crossings_spikes(signal, fs, threshold_from, threshold_to, dead_time):
    dead_time_idx = dead_time * fs
    if not threshold_to:
      threshold_to=np.min(signal)
    threshold_crossings = np.diff(((signal <= threshold_from) & (signal>=threshold_to)).astype(int) > 0).nonzero()[0]
    distance_sufficient = np.insert(np.diff(threshold_crossings) >= dead_time_idx, 0, True)

    while not np.all(distance_sufficient):
        # repeatedly remove all threshold crossings that violate the dead_time
        threshold_crossings = threshold_crossings[distance_sufficient]
        distance_sufficient = np.insert(np.diff(threshold_crossings) >= dead_time_idx, 0, True)
    return threshold_crossings

def _get_next_minimum(signal, index, max_samples_to_search):
    search_end_idx = min(index + max_samples_to_search, signal.shape[0])
    min_idx = np.argmin(signal[index:search_end_idx])
    return index + min_idx

def _align_to_minimum(signal, fs, threshold_crossings, search_range):
    search_end = int(search_range*fs)
    aligned_spikes = [_get_next_minimum(signal, t, search_end) for t in threshold_crossings]
    return np.array(aligned_spikes)

def _filter_base_freqeuncy(signal_in_uV, time_in_sec, High_pass, Low_pass):    
    F = fft(signal_in_uV)
    F[(len(time_in_sec)//2+1):] = 0
    if High_pass:
        F[:int(High_pass)] = 0
    if Low_pass:
        F[int(Low_pass):] = 0
 
    x_returned=ifft(F)
    return x_returned

def _path_valid(file_path):
    try:
        _file = McsPy.McsData.RawData(file_path)
    except:
        return 0
    return _file

def _get_proper_threshold (signal, threshold_from, is_spike) :
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
    return threshold_from

def _get_pca_labels(cutouts, n_components):
    pca = PCA()
    pca.n_components = int(n_components)
    scaler = StandardScaler()
    scaled_cutouts = scaler.fit_transform(abs(cutouts))
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

def _signal_average_around_stimulus(signal, stimulus_df, pre, post, fs):
    temp = pd.DataFrame()
    pre_idx = int(pre * fs)
    post_idx = int(post * fs)

    for i in range(0,len(stimulus_df)) :
        index1 = stimulus_df["start"][i]
        index2 = stimulus_df["end"][i]
        if index1-pre_idx >= 0 and index2+post_idx <= signal.shape[0]:
            oneWaveform = np.concatenate((signal[(index1-pre_idx):index1],signal[index2:(index2+post_idx)]),axis=None) 
        if i==0:
            waveform_df=pd.DataFrame(oneWaveform)
            temp.append(waveform_df)
        else:
            waveform_df[0] += oneWaveform
    return waveform_df/(len(stimulus_df))*1000000

def _get_spike_info(electrode_stream, channel_id, signal, threshold_from, threshold_to, dead_time):
    fs = int(electrode_stream.channel_infos[channel_id].sampling_frequency.magnitude)
    crossings = _detect_threshold_crossings_spikes(signal, fs, threshold_from, threshold_to, dead_time) # dead time of 3 ms
    spks = _align_to_minimum(signal, fs, crossings, 0.002) # search range 2 ms
    return fs, spks

def _detect_threshold_crossings_stimulus(signal, fs, threshold, dead_time):
    dead_time_idx = dead_time * fs
    threshold_crossings = np.diff((signal <= threshold)).nonzero()[0]
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


# main functions

def plot_signal(file_path, channel_id, from_in_s, to_in_s, canvas, suplot_num, high_pass, low_pass):
    _file = _path_valid(file_path)
    if not _file:
        return 1, "File path is incorrect"

    analog_stream = _file.recordings[0].analog_streams[0]
    if channel_id not in analog_stream.channel_infos:
        return 1, "Channel ID is incorrect"   
    
    signal_in_uV, time_in_sec = _get_signal_time(analog_stream, channel_id, from_in_s, to_in_s)

    if (high_pass!=None) or (low_pass!=None):
        signal_in_uV = _filter_base_freqeuncy(signal_in_uV, time_in_sec, high_pass, low_pass)
    
    axes = canvas.figure.get_axes()
    ax = axes[suplot_num]
    ax.clear()
    ax.plot(time_in_sec, signal_in_uV, linewidth=0.5)

    ax.set_xlabel('Time (%s)' % ureg.s)
    ax.set_ylabel('Voltage (%s)' % ureg.uV)
    ax.set_title('Channel %s' % channel_id)

    canvas.figure.tight_layout()
    canvas.draw()
    return 0,""

def plot_all_spikes_together(file_path, channel_id, n_components, pre, post, dead_time, number_spikes, canvas, suplot_num,
                        from_in_s, to_in_s, high_pass, low_pass, threshold_from, threshold_to):  
    _file = _path_valid(file_path)
    if not _file:
        return 1, "File path is incorrect"
    
    electrode_stream = _file.recordings[0].analog_streams[0]
    if channel_id not in electrode_stream.channel_infos:
        return 1, "Channel ID is incorrect"

    if n_components == None:
        n_components = 1

    signal_in_uV, time_in_sec = _get_signal_time(electrode_stream, channel_id, 0, None)
    if (high_pass!=None) or (low_pass!=None):
        signal_in_uV = _filter_base_freqeuncy(signal_in_uV, time_in_sec, high_pass, low_pass)

    threshold_from = _get_proper_threshold(signal_in_uV, threshold_from, True)
    fs, spks = _get_spike_info(electrode_stream, channel_id, signal_in_uV, threshold_from, threshold_to, dead_time)
    if (len(spks)<=1):
        return 1, "spike filter is not correct"

    cutouts = _get_signal_cutouts(signal_in_uV, fs, spks, pre, post)
    labels=_get_pca_labels(cutouts, n_components)
    
    axes = canvas.figure.get_axes()
    ax = axes[suplot_num]
    ax.clear()
    for i in range(int(n_components)):
        idx = labels == i
        color = plt.rcParams['axes.prop_cycle'].by_key()['color'][i]
        _plot_each_spike(ax, cutouts[idx,:], fs, pre, post, n=number_spikes, color=color)
    canvas.figure.tight_layout()
    canvas.draw()
    return 0, ""

def plot_stimulus_average(file_path, channel_id, dead_time, stimulus_threshold, pre, post, canvas, suplot_num):
    _file = _path_valid(file_path)
    if not _file:
        return 1, "File path is incorrect"

    electrode_stream = _file.recordings[0].analog_streams[0]
    if channel_id not in electrode_stream.channel_infos:
        return 1, "Channel ID is incorrect"  

    _channel_info = electrode_stream.channel_infos[0]
    fs = _channel_info.sampling_frequency.magnitude
    signal = electrode_stream.get_channel_in_range(channel_id, 0, electrode_stream.channel_data.shape[1])[0]

    if not stimulus_threshold:
        stimulus_threshold = -0.0001
    thresholds=_detect_threshold_crossings_stimulus(signal, fs, stimulus_threshold, dead_time)
    stimulus_df=pd.DataFrame(columns={"start","end"})
    stimulus_df["start"]=[int(thresholds[i]) for i in range(0,len(thresholds)) if i%2==0]
    try:
        stimulus_df["end"]=[int(thresholds[i]) for i in range(0,len(thresholds)) if i%2==1]
        if (len(stimulus_df)==0):
            return 1, "incorrect filter"
    except:
        return 1,"incorrect filter"

    df_to_draw = _signal_average_around_stimulus(signal, stimulus_df, pre, post, fs)
    x=np.linspace(-pre,post,len(df_to_draw))
    xx=[0,0]
    yx=[df_to_draw.max(),df_to_draw.min()]
    axes = canvas.figure.get_axes()
    ax = axes[suplot_num]
    ax.clear()
    ax.plot(x, df_to_draw[0], linewidth=2)
    ax.plot(xx, yx, linewidth=2)
    
    ax.set_xlabel('Time (%s)' % ureg.s)
    ax.set_ylabel('Voltage (%s)' % ureg.uV)
    canvas.figure.tight_layout()
    canvas.draw()
    return 0,""

def plot_signal_with_spikes_or_stimulus(file_path, channel_id, canvas, suplot_num, is_spike, from_in_s, to_in_s, 
                                        threshold_from, threshold_to, dead_time):
    _file = _path_valid(file_path)
    if not _file:
        return 1, "File path is incorrect"

    electrode_stream = _file.recordings[0].analog_streams[0]
    if channel_id not in electrode_stream.channel_infos:
        return 1, "Channel ID is incorrect"   
    
    sampling_frequency = electrode_stream.channel_infos[channel_id].sampling_frequency.magnitude  
    from_idx ,to_idx = _check_time_range(electrode_stream,sampling_frequency,from_in_s,to_in_s)
    
    signal_in_uV, time_in_sec = _get_signal_time(electrode_stream, channel_id, from_in_s, to_in_s) # need this to draw signal
    signal = signal_in_uV/1000000 # need this to calculate stimulus or spikes
    threshold_from = _get_proper_threshold(signal, threshold_from,is_spike)
    if is_spike:
        fs, spks = _get_spike_info(electrode_stream, channel_id, signal, threshold_from, threshold_to, dead_time)
    else :
        fs = int(electrode_stream.channel_infos[channel_id].sampling_frequency.magnitude)
        spks = _detect_threshold_crossings_stimulus(signal,fs,threshold_from,dead_time)

    timestamps = spks / fs
    range_in_s = (from_idx, to_idx)
    spikes_in_range = timestamps[(timestamps >= range_in_s[0]) & (timestamps <= range_in_s[1])]
    
    axes = canvas.figure.get_axes()
    ax = axes[suplot_num]
    ax.clear()
    ax.plot(time_in_sec, signal_in_uV, linewidth=0.5, color = "darkmagenta")
    ax.plot(spikes_in_range, [threshold_from*1e6]*spikes_in_range.shape[0], 'ro', ms=2)

    ax.set_xlabel('Time (%s)' % ureg.s)
    ax.set_ylabel('Voltage (%s)' % ureg.uV)
    ax.set_title('Channel %s' % channel_id)
    canvas.figure.tight_layout()
    canvas.draw()
    return 0,""

def plot_signal_frequencies(file_path, channel_id, canvas, suplot_num, from_in_s, to_in_s):
    _file = _path_valid(file_path)
    if not _file:
        return 1, "File path is incorrect"

    electrode_stream = _file.recordings[0].analog_streams[0]
    if channel_id not in electrode_stream.channel_infos:
        return 1, "Channel ID is incorrect"   
    
    signal_in_uV, time_in_sec = _get_signal_time(electrode_stream, channel_id, from_in_s, to_in_s)
    X = fft(signal_in_uV)
    X[(len(time_in_sec)//2+1):]=0

    axes = canvas.figure.get_axes()
    ax = axes[suplot_num]
    ax.clear()
    ax.plot(abs(X[1:]), linewidth=0.5, color = "darkorange")
    
    ax.set_xlabel('Frequency (Hz)')
    canvas.figure.tight_layout()
    canvas.draw()
    return 0,""

def extract_waveform(analog_stream_path, file_save_path, stream_id=0, channel_id=None, from_in_s=0, to_in_s=None):   
    _file = _path_valid(analog_stream_path)
    if not _file:
        return 1, "File path is incorrect"

    # TODO
    analog_stream = _file.recordings[0].analog_streams[stream_id]
    _channel_info = analog_stream.channel_infos[0]
    sampling_frequency = _channel_info.sampling_frequency.magnitude
    from_idx ,to_idx = _check_time_range(analog_stream,sampling_frequency,from_in_s,to_in_s)  # get start and end index
    time = analog_stream.get_channel_sample_timestamps(0, from_idx, to_idx)  # get the timestamps for each sample 
    scale_factor_for_second = Q_(1,time[1]).to(ureg.s).magnitude  # scale time to seconds
    time_in_sec = time[0] * scale_factor_for_second
    df=pd.DataFrame()
    df["time_in_sec"] = time_in_sec

    if (channel_id==None):
        for channel in analog_stream.channel_infos:       
            df["signal for "+str(channel)] = _get_specific_channel_signal(analog_stream,channel,from_idx,to_idx)
    else:
        if channel_id in analog_stream.channel_infos:
            df["signal for "+str(channel_id)] = _get_specific_channel_signal(analog_stream,channel_id,from_idx,to_idx)
        else:
            return 1, "Wrong channel_id !"

    df.to_csv(file_save_path,index=False)
    return 0, ""

def extract_stimulus(analog_stream_path, file_save_path, channel_id, stimulus_threshold, dead_time):
    _file = _path_valid(analog_stream_path)
    if not _file:
        return 1, "File path is incorrect"

    analog_stream = _file.recordings[0].analog_streams[0]
    _channel_info = analog_stream.channel_infos[0]
    fs = _channel_info.sampling_frequency.magnitude
    signal = analog_stream.get_channel_in_range(channel_id, 0, analog_stream.channel_data.shape[1])[0]
    threshold_from = _get_proper_threshold(signal, stimulus_threshold, False)
    thresholds = _detect_threshold_crossings_stimulus(signal, fs, threshold_from, dead_time)/fs
    stimulus_in_second_df = pd.DataFrame(columns=["start","end"])
    stimulus_in_second_df["start"] = [thresholds[i] for i in range(0,len(thresholds),2)]
    stimulus_in_second_df["end"] = [thresholds[i] for i in range(1,len(thresholds),2)]
    stimulus_in_second_df["stimulus_time"] = (stimulus_in_second_df["end"] - stimulus_in_second_df["start"])
    stimulus_in_second_df["stimulus_number"] = np.ceil(stimulus_in_second_df["stimulus_time"] / 0.02)
    stimulus_in_second_df["frequency"] = stimulus_in_second_df["stimulus_number"] / stimulus_in_second_df["stimulus_time"]
    stimulus_in_second_df.to_csv(file_save_path, index = False)
    return 0, ""

def extract_spike(analog_stream_path, file_save_path, channel_id, threshold_from, threshold_to, dead_time):
    _file = _path_valid(analog_stream_path)
    if not _file:
        return 1, "File path is incorrect"

    analog_stream = _file.recordings[0].analog_streams[0]
    if channel_id not in analog_stream.channel_infos:
        return 1, "Channel ID is incorrect"  

    signal = analog_stream.get_channel_in_range(channel_id, 0, analog_stream.channel_data.shape[1])[0]

    threshold_from = _get_proper_threshold(signal, threshold_from, True)
    fs, spks = _get_spike_info(analog_stream, channel_id, signal, threshold_from, threshold_to, dead_time)
    spikes_in_second=[]
    for spike in spks:
        temp_time = analog_stream.get_channel_sample_timestamps(channel_id, spike, spike)[0][0]/1000000
        spikes_in_second.append(temp_time)
    spikes_in_second_df = pd.DataFrame(spikes_in_second, columns={"spike_time"})
    spikes_in_second_df.to_csv(file_save_path, index=False)
    return 0, ""

def get_all_channel_ids(file_path):
    _file = _path_valid(file_path)
    if not _file:
        return 1, "File path is incorrect"
    keys = [str(value.channel_id) for key, value in _file.recordings[0].analog_streams[0].channel_infos.items()]
    return 0, keys

