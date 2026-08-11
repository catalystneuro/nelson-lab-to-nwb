from pathlib import Path
import numpy as np
from pydantic import DirectoryPath
from neo.rawio import IntanRawIO


def find_rising_times(signal, sampling_rate):
    signal = np.array(signal)
    rising_indices = np.where(np.diff(signal) == 1)[0]
    rising_times = (rising_indices + 1) / sampling_rate
    return rising_times


def get_ttl_signal(neo_reader, ttl_signal_name="DIGITAL-IN-14"):
    # Find ttl signal stream id
    for s in neo_reader.header["signal_channels"]:
        if s[0] == ttl_signal_name:
            ttl_signal_id = s[1]
            ttl_signal_sampling_rate = s[2]
            ttl_signal_stream_id = s[7]

    # Find ttl signal stream index
    for ii, s in enumerate(neo_reader.header["signal_streams"]):
        if s[1] == ttl_signal_stream_id:
            ttl_signal_stream_index = ii

    ttl_signal = neo_reader.get_analogsignal_chunk(
        stream_index=ttl_signal_stream_index, channel_names=[ttl_signal_name]
    )
    return ttl_signal.flatten(), ttl_signal_sampling_rate


def extract_ttl_times(
    folder_path: DirectoryPath,
    ttl_signal_name: str = "DIGITAL-IN-14",
):
    """
    Rising-edge times of one Intan digital line, concatenated across a split session.

    NeuroConv's `IntanDigitalInterface` reads the same lines but only to write them as an
    events table; it exposes no accessor for the times, so the alignment still reads them here.
    """
    list_of_files = sorted([str(f.resolve()) for f in Path(folder_path).glob("*.rhd")])
    ttl_signal_full = np.array([])
    for file in list_of_files:
        neo_reader = IntanRawIO(filename=file)
        neo_reader.parse_header()
        ttl_signal, ttl_sampling_rate = get_ttl_signal(neo_reader=neo_reader, ttl_signal_name=ttl_signal_name)
        ttl_signal_full = np.concatenate((ttl_signal_full, ttl_signal))
    return find_rising_times(signal=ttl_signal_full, sampling_rate=ttl_sampling_rate)
