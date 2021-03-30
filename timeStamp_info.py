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