from typing import Dict, Optional, Literal
from neuroconv.utils.dict import DeepDict
import numpy as np
from datetime import datetime
from neuroconv.datainterfaces import (
    BlackrockRecordingInterface,
    BlackrockSortingInterface,
    VideoInterface,
)
from neuroconv import NWBConverter
from neuroconv.utils import dict_deep_update

from nelson_lab_to_nwb.interfaces import CognitiveBehavioralInterface
from nelson_lab_to_nwb.utils.probe import set_probe


class BlackrockNWBConverter(NWBConverter):
    """
    Primary conversion class for Blackrock recording and sorting data,
    plus behavioral events and video from Nelson lab.
    """

    data_interface_classes = dict(
        BlackrockRaw=BlackrockRecordingInterface,
        BlackrockLFP=BlackrockRecordingInterface,
        BlackrockSorting=BlackrockSortingInterface,
        BehavioralEvents=CognitiveBehavioralInterface,
        BehavioralVideo=VideoInterface,
    )

    def __init__(
        self,
        source_data: Dict[str, dict],
        probe_type: Literal["type_1", "type_2"] = "type_1",
        user_metadata: Optional[dict] = None,
        verbose: bool = True,
    ):
        super().__init__(source_data=source_data, verbose=verbose)

        # Add probe information: https://probeinterface.readthedocs.io/en/main/index.html
        if "BlackrockRaw" in self.data_interface_objects:
            set_probe(
                extractor=self.data_interface_objects["BlackrockRaw"].recording_extractor,
                probe_type=probe_type,
            )
        if "BlackrockLFP" in self.data_interface_objects:
            set_probe(
                extractor=self.data_interface_objects["BlackrockLFP"].recording_extractor,
                probe_type=probe_type,
            )
        self.user_metadata = user_metadata or {}

    def get_metadata(self) -> DeepDict:
        source_metadata = super().get_metadata()
        metadata = dict_deep_update(source_metadata, self.user_metadata)
        return metadata

    def temporally_align_data_interfaces(
        self,
        metadata: dict,
        conversion_options: Optional[dict] = None,
    ):
        # Runs alignment only if session_start_time is not present in user metadata
        if self.user_metadata.get("NWBFile", {}).get("session_start_time", None) is None:
            # Align video timestamps
            if "BehavioralVideo" in self.data_interface_objects:
                neo_reader = self.data_interface_objects["BlackrockSorting"].sorting_extractor.neo_reader
                ttl_id = 4
                laser_id = 2
                digital_events_sampling_rate = 30000

                digital_events_times = neo_reader.get_event_timestamps(event_channel_index=0)[0].astype("int")
                digital_events_values = neo_reader.get_event_timestamps(event_channel_index=0)[2].astype("int")
                laser_times = digital_events_times[np.where(digital_events_values == laser_id)[0]]
                ttl_times = digital_events_times[np.where(digital_events_values == ttl_id)[0]]
                ttl_times_filtered = ttl_times[ttl_times <= laser_times[0]] / digital_events_sampling_rate

                video_interface = self.data_interface_objects["BehavioralVideo"]
                print(f"Setting aligned timestamps for video {video_interface.metadata_key_name}.")
                video_interface.set_aligned_timestamps(aligned_timestamps=[ttl_times_filtered])

            # Align Ecephys interfaces
            nwbfile_session_start_time = datetime.fromisoformat(metadata["NWBFile"].get("session_start_time"))
            ecephys_interfaces = [
                "BlackrockRaw",
                "BlackrockLFP",
                "BlackrockSorting",
            ]

            for interface_name in ecephys_interfaces:
                if interface_name in self.data_interface_objects:
                    ecephys_interface = self.data_interface_objects[interface_name]
                    ecephys_interface_metadata = ecephys_interface.get_metadata()
                    if "session_start_time" in ecephys_interface_metadata["NWBFile"]:
                        ecephys_interface_session_start_time = datetime.fromisoformat(ecephys_interface_metadata["NWBFile"].get("session_start_time"))
                        time_delta = (ecephys_interface_session_start_time - nwbfile_session_start_time).total_seconds()
                        print(f"Setting aligned timestamps for {interface_name}")
                        ecephys_interface.set_aligned_starting_time(aligned_starting_time=time_delta)
