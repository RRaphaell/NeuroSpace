from McsPy import ureg, Q_


def check_time_range(analog_stream, sampling_frequency, from_in_s, to_in_s):
    signal_shape = analog_stream.channel_data.shape[1]

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


def get_signal_time(analog_stream, channel_id, from_in_s, to_in_s):
    channel_info = analog_stream.channel_infos[channel_id]
    sampling_frequency = channel_info.sampling_frequency.magnitude
    from_idx, to_idx = check_time_range(analog_stream, sampling_frequency, from_in_s, to_in_s)
    time = analog_stream.get_channel_sample_timestamps(channel_id, from_idx, to_idx)
    signal = analog_stream.get_channel_in_range(channel_id, from_idx, to_idx)
    scale_factor_for_second = Q_(1, time[1]).to(ureg.s).magnitude
    time_in_sec = time[0] * scale_factor_for_second
    scale_factor_for_uv = Q_(1, signal[1]).to(ureg.uV).magnitude
    signal_in_uv = signal[0] * scale_factor_for_uv
    return signal_in_uv, time_in_sec
