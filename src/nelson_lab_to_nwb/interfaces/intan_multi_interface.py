from pathlib import Path
import numpy as np
from pydantic import DirectoryPath
from neuroconv.datainterfaces import IntanRecordingInterface
from neo.rawio import IntanRawIO

from nelson_lab_to_nwb.utils.probe import set_probe


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


class IntanMultifilesRecordingInterface(IntanRecordingInterface):
    """
    Interface for an Intan session saved across multiple .rhd files.

    The concatenation is done by NeuroConv's own `saved_files_are_split` option; this class
    only adds the lab's probe geometry and the TTL extraction used to align the videos.
    """

    display_name = "Intan Recording"
    associated_suffixes = (".rhd", ".rhs")
    info = "Interface for Intan recording data."

    def __init__(
        self,
        folder_path: DirectoryPath,
        verbose: bool = True,
        es_key: str = "ElectricalSeries",
    ):
        """
        Load and prepare raw data and corresponding metadata from the Intan format (.rhd or .rhs files).

        Parameters
        ----------
        folder_path : DirectoryPath
            Path to the folder containing the rhd or rhs files.
        verbose : bool, default: True
            Verbose
        es_key : str, default: "ElectricalSeries"
        """
        self.folder_path = Path(folder_path)
        rhd_file_paths = sorted(self.folder_path.glob("*.rhd"))
        if not rhd_file_paths:
            raise FileNotFoundError(f"No .rhd files found in {self.folder_path}.")

        super().__init__(
            file_path=rhd_file_paths[0],
            saved_files_are_split=True,
            verbose=verbose,
            es_key=es_key,
        )

        # Add probe information: https://probeinterface.readthedocs.io/en/main/index.html
        set_probe(self.recording_extractor)

    def extract_ttl_times(
        self,
        ttl_signal_name: str = "DIGITAL-IN-14",
    ):
        list_of_files = sorted([str(f.resolve()) for f in self.folder_path.glob("*.rhd")])
        ttl_signal_full = np.array([])
        for file in list_of_files:
            neo_reader = IntanRawIO(filename=file)
            neo_reader.parse_header()
            ttl_signal, ttl_sampling_rate = get_ttl_signal(neo_reader=neo_reader, ttl_signal_name=ttl_signal_name)
            ttl_signal_full = np.concatenate((ttl_signal_full, ttl_signal))
        ttl_times_full = find_rising_times(signal=ttl_signal_full, sampling_rate=ttl_sampling_rate)
        return ttl_times_full
