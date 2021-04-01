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

def check_time_range(analog_stream,sampling_frequency,from_in_s,to_in_s):
    from_idx = max(0, int(from_in_s * sampling_frequency))
    if to_in_s is None:
        to_idx = analog_stream.channel_data.shape[1]
    else:
        to_idx = min(analog_stream.channel_data.shape[1], int(to_in_s * sampling_frequency))
    return from_idx, to_idx

def iterate_per_channel(analog_stream,channel_id,from_idx,to_idx):
    signal = analog_stream.get_channel_in_range(channel_id, from_idx, to_idx) # get the signal 
    signal_in_uV = signal[0] * Q_(1,signal[1]).to(ureg.uV).magnitude # scale signal to µV
    return signal_in_uV

def save_channel_info(analog_stream_path, file_save_path, stream_id = 0, channel_id=None, from_in_s=0, to_in_s=None):   
    try:
        file_ = McsPy.McsData.RawData(analog_stream_path)
    except:
        return 1, "File path is incorrect"
    analog_stream = file_.recordings[0].analog_streams[stream_id]
    _channel_info = analog_stream.channel_infos[0]
    sampling_frequency = _channel_info.sampling_frequency.magnitude
    from_idx ,to_idx = check_time_range(analog_stream,sampling_frequency,from_in_s,to_in_s)  # get start and end index
    time = analog_stream.get_channel_sample_timestamps(0, from_idx, to_idx)  # get the timestamps for each sample 
    scale_factor_for_second = Q_(1,time[1]).to(ureg.s).magnitude  # scale time to seconds
    time_in_sec = time[0] * scale_factor_for_second
    df=pd.DataFrame()
    df["time_in_sec"]=time_in_sec
    if(channel_id==None):
        for channel in analog_stream.channel_infos:       
            df["signal for "+str(channel)]=iterate_per_channel(analog_stream,channel,from_idx,to_idx)
    else:
        if channel_id in analog_stream.channel_infos:
            df["signal for "+str(channel_id)]=iterate_per_channel(analog_stream,channel_id,from_idx,to_idx)
        else:
            return 1, "Wrong channel_id !"
    df.to_csv(file_save_path,index=False)
    return 0, ""

def extract_waveforms(signal, fs, spikes_idx, pre, post):
    cutouts = []
    pre_idx = int(pre * fs)
    post_idx = int(post * fs)
    for index in spikes_idx:
        if index-pre_idx >= 0 and index+post_idx <= signal.shape[0]:
            cutout = signal[(index-pre_idx):(index+post_idx)]
            cutouts.append(cutout)
    return np.stack(cutouts)

def plot_waveforms(cutouts, fs, pre, post, n=100, color='k', show=True):
    if n is None:
        n = cutouts.shape[0]
    n = min(n, cutouts.shape[0])
    time_in_us = np.arange(-pre*1000, post*1000, 1e3/fs)
    if show:
        _ = plt.figure(figsize=(12,6))
    
    for i in range(n):
        _ = plt.plot(time_in_us, cutouts[i,]*1e6, color, linewidth=1, alpha=0.3)
        _ = plt.xlabel('Time (%s)' % ureg.ms)
        _ = plt.ylabel('Voltage (%s)' % ureg.uV)
        _ = plt.title('Cutouts')

    if show:
        plt.show()

def detect_threshold_crossings(signal, fs, threshold, dead_time):
    dead_time_idx = dead_time * fs
    threshold_crossings = np.diff((signal <= threshold).astype(int) > 0).nonzero()[0]
    distance_sufficient = np.insert(np.diff(threshold_crossings) >= dead_time_idx, 0, True)
    while not np.all(distance_sufficient):
        # repeatedly remove all threshold crossings that violate the dead_time
        threshold_crossings = threshold_crossings[distance_sufficient]
        distance_sufficient = np.insert(np.diff(threshold_crossings) >= dead_time_idx, 0, True)
    return threshold_crossings

def get_next_minimum(signal, index, max_samples_to_search):
    search_end_idx = min(index + max_samples_to_search, signal.shape[0])
    min_idx = np.argmin(signal[index:search_end_idx])
    return index + min_idx

def align_to_minimum(signal, fs, threshold_crossings, search_range):
    search_end = int(search_range*fs)
    aligned_spikes = [get_next_minimum(signal, t, search_end) for t in threshold_crossings]
    return np.array(aligned_spikes)
  
def draw_channel_spikes(file_path,channel_id,n_components,pre,post,dead_time,number_spikes):  
    
    try:
        _file = McsPy.McsData.RawData(file_path)
    except:
        return 1, "File path is incorrect"
    
    electrode_stream = _file.recordings[0].analog_streams[0]
    if channel_id not in analog_stream.channel_infos:
        return 1, "Channel ID is incorrect"
    
    signal = electrode_stream.get_channel_in_range(channel_id, 0, electrode_stream.channel_data.shape[1])[0]
    noise_std = np.std(signal)
    noise_mad = np.median(np.absolute(signal)) / 0.6745
    spike_threshold = -5 * noise_mad # roughly -30 µV
    fs = int(electrode_stream.channel_infos[channel_id].sampling_frequency.magnitude)
    crossings = detect_threshold_crossings(signal, fs, spike_threshold, dead_time) # dead time of 3 ms
    spks = align_to_minimum(signal, fs, crossings, 0.002) # search range 2 ms
    cutouts = extract_waveforms(signal, fs, spks, pre, post)
    pca = PCA()
    pca.n_components = n_components
    scaler = StandardScaler()
    scaled_cutouts = scaler.fit_transform(cutouts)
    transformed = pca.fit_transform(scaled_cutouts)
    gmm = GaussianMixture(n_components=n_components, n_init=10)
    labels = gmm.fit_predict(transformed)
    _ = plt.figure(figsize=(8,8))
    for i in range(n_components):
        idx = labels == i
        color = plt.rcParams['axes.prop_cycle'].by_key()['color'][i]
        plot_waveforms(cutouts[idx,:], fs, pre, post, n=number_spikes, color=color, show=False)
    plt.show()

def plot_analog_stream_channel(file_path, channel_id, from_in_s, to_in_s, canvas,figure):
    try:
        _file = McsPy.McsData.RawData(file_path)
    except:
        return 1, "File path is incorrect"

    analog_stream = _file.recordings[0].analog_streams[0]
    if channel_id not in analog_stream.channel_infos:
        return 1, "Channel ID is incorrect"   
    ids = [c.channel_id for c in analog_stream.channel_infos.values()]
    channel_info = analog_stream.channel_infos[channel_id]
    sampling_frequency = channel_info.sampling_frequency.magnitude  
    from_idx ,to_idx = check_time_range(analog_stream,sampling_frequency,from_in_s,to_in_s)  # get start and end index       
    time = analog_stream.get_channel_sample_timestamps(channel_id, from_idx, to_idx)

    scale_factor_for_second = Q_(1,time[1]).to(ureg.s).magnitude
    time_in_sec = time[0] * scale_factor_for_second
    signal = analog_stream.get_channel_in_range(channel_id, from_idx, to_idx)
    scale_factor_for_uV = Q_(1,signal[1]).to(ureg.uV).magnitude
    signal_in_uV = signal[0] * scale_factor_for_uV

    figure.clear()
    ax = figure.add_subplot()
    ax.plot(time_in_sec, signal_in_uV,linewidth=0.5)

    ax.set_xlabel('Time (%s)' % ureg.s)
    ax.set_ylabel('Voltage (%s)' % ureg.uV)
    ax.set_title('Channel %s' % channel_info.info['Label'])

    canvas.draw()
    return 0,""