from pathlib import Path
import numpy as np
from packaging.version import Version
from pynwb.ecephys import ElectricalSeries
from neuroconv.utils import DirectoryPath, get_schema_from_hdmf_class
from neuroconv.tools import get_package_version
from neuroconv.datainterfaces.ecephys.baserecordingextractorinterface import BaseRecordingExtractorInterface
from spikeinterface.extractors import read_intan
from spikeinterface import concatenate_recordings
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
        stream_index=ttl_signal_stream_index,
        channel_names=[ttl_signal_name]
    )
    return ttl_signal.flatten(), ttl_signal_sampling_rate


def make_concatenate_extractor(
    folder_path: DirectoryPath,
    stream_id: str = "0",
):
    list_of_files = sorted([str(f.resolve()) for f in Path(folder_path).glob("*.rhd")])
    list_of_recordings = []
    for file in list_of_files:
        rec = read_intan(file_path=file, stream_id=stream_id)
        list_of_recordings.append(rec)
    return concatenate_recordings(list_of_recordings)


def extract_electrode_metadata(recording_extractor) -> dict:
    neo_version = get_package_version(name="neo")
    # The native native_channel_name in Intan have the following form: A-000, A-001, A-002, B-000, B-001, B-002, etc.
    if neo_version > Version("0.13.0"):  # TODO: Remove after the release of neo 0.14.0
        native_channel_names = recording_extractor.get_channel_ids()
    else:
        # Previous to version 0.13.1 the native_channel_name was stored as channel_name
        native_channel_names = recording_extractor.get_property("channel_name")
    group_names = [channel.split("-")[0] for channel in native_channel_names]
    unique_group_names = set(group_names)
    group_electrode_numbers = [int(channel.split("-")[1]) for channel in native_channel_names]
    custom_names = list()
    electrodes_metadata = dict(
        group_names=group_names,
        unique_group_names=unique_group_names,
        group_electrode_numbers=group_electrode_numbers,
        custom_names=custom_names,
    )
    return electrodes_metadata


class IntanMultifilesRecordingInterface(BaseRecordingExtractorInterface):
    """
    Primary data interface class for converting Intan data from multiple files using the

    :py:class:`~spikeinterface.extractors.IntanRecordingExtractor`.
    """

    display_name = "Intan Recording"
    associated_suffixes = (".rhd", ".rhs")
    info = "Interface for Intan recording data."
    stream_id = "0"  # This is the only stream_id of Intan that might have neural data

    @classmethod
    def get_extractor(cls):
        cls.Extractor = make_concatenate_extractor
        return make_concatenate_extractor

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

        super().__init__(folder_path=folder_path, stream_id=self.stream_id, verbose=verbose, es_key=es_key)
        electrodes_metadata = extract_electrode_metadata(recording_extractor=self.recording_extractor)

        group_names = electrodes_metadata["group_names"]
        group_electrode_numbers = electrodes_metadata["group_electrode_numbers"]
        unique_group_names = electrodes_metadata["unique_group_names"]
        custom_names = electrodes_metadata["custom_names"]

        channel_ids = self.recording_extractor.get_channel_ids()
        self.recording_extractor.set_property(key="group_name", ids=channel_ids, values=group_names)
        if len(unique_group_names) > 1:
            self.recording_extractor.set_property(
                key="group_electrode_number", ids=channel_ids, values=group_electrode_numbers
            )

        if any(custom_names):
            self.recording_extractor.set_property(key="custom_channel_name", ids=channel_ids, values=custom_names)

        # Add probe information: https://probeinterface.readthedocs.io/en/main/index.html
        set_probe(self.recording_extractor)

    def extract_ttl_times(
        self,
        ttl_signal_name: str = "DIGITAL-IN-14",
    ):
        folder_path = self.source_data["folder_path"]
        list_of_files = sorted([str(f.resolve()) for f in Path(folder_path).glob("*.rhd")])
        ttl_signal_full = np.array([])
        for file in list_of_files:
            neo_reader = IntanRawIO(filename=file)
            neo_reader.parse_header()
            ttl_signal, ttl_sampling_rate = get_ttl_signal(neo_reader=neo_reader, ttl_signal_name=ttl_signal_name)
            ttl_signal_full = np.concatenate((ttl_signal_full, ttl_signal))
        ttl_times_full = find_rising_times(signal=ttl_signal_full, sampling_rate=ttl_sampling_rate)
        return ttl_times_full

    def get_metadata_schema(self) -> dict:
        metadata_schema = super().get_metadata_schema()
        metadata_schema["properties"]["Ecephys"]["properties"].update(
            ElectricalSeriesRaw=get_schema_from_hdmf_class(ElectricalSeries)
        )
        return metadata_schema

    def get_metadata(self) -> dict:
        metadata = super().get_metadata()
        ecephys_metadata = metadata["Ecephys"]

        # Add device
        device = dict(
            name="Intan",
            description="Intan recording",
            manufacturer="Intan",
        )
        device_list = [device]
        ecephys_metadata.update(Device=device_list)

        # Add electrode group
        unique_group_name = set(self.recording_extractor.get_property("group_name"))
        electrode_group_list = [
            dict(
                name=group_name,
                description=f"Group {group_name} electrodes.",
                device="Intan",
                location="",
            )
            for group_name in unique_group_name
        ]
        ecephys_metadata.update(ElectrodeGroup=electrode_group_list)

        # Add electrodes and electrode groups
        ecephys_metadata.update(
            Electrodes=[
                dict(name="group_name", description="The name of the ElectrodeGroup this electrode is a part of.")
            ],
            ElectricalSeriesRaw=dict(name="ElectricalSeriesRaw", description="Raw acquisition traces."),
        )

        # Add group electrode number if available
        recording_extractor_properties = self.recording_extractor.get_property_keys()
        if "group_electrode_number" in recording_extractor_properties:
            ecephys_metadata["Electrodes"].append(
                dict(name="group_electrode_number", description="0-indexed channel within a group.")
            )
        if "custom_channel_name" in recording_extractor_properties:
            ecephys_metadata["Electrodes"].append(
                dict(name="custom_channel_name", description="Custom channel name assigned in Intan.")
            )

        return metadata
