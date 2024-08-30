from typing import Dict
import numpy as np
from neuroconv.datainterfaces import BlackrockRecordingInterface, BlackrockSortingInterface, VideoInterface
from neuroconv import NWBConverter

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

    def __init__(self, source_data: Dict[str, dict], verbose: bool = True):
        super().__init__(source_data=source_data, verbose=verbose)

        # Add probe information: https://probeinterface.readthedocs.io/en/main/index.html
        set_probe(self.data_interface_objects["BlackrockRaw"].recording_extractor)
        set_probe(self.data_interface_objects["BlackrockLFP"].recording_extractor)

    def temporally_align_data_interfaces(self):
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
