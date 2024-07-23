from nelson_lab_to_nwb.interfaces import (
    IntanMultifilesRecordingInterface,
    AIMScoreInterface
)
from neuroconv import NWBConverter
from neuroconv.datainterfaces import VideoInterface


class IntanSessionNWBConverter(NWBConverter):
    """Primary conversion class for Intan recording + behavioral data."""

    data_interface_classes = dict(
        IntanMultifilesRaw=IntanMultifilesRecordingInterface,
        AIMScore=AIMScoreInterface,
        BehavioralVideoTop=VideoInterface,
        BehavioralVideoSide=VideoInterface,
    )

    def temporally_align_data_interfaces(self):
        # Extract TTL times from Intan data and set aligned timestamps for video data
        intan_interface = self.data_interface_objects["IntanMultifilesRaw"]
        ttl_times = intan_interface.extract_ttl_times()

        video_interface_top = self.data_interface_objects["BehavioralVideoTop"]
        print(f"Setting aligned timestamps for video {video_interface_top.metadata_key_name}.")
        video_interface_top.set_aligned_timestamps(aligned_timestamps=[ttl_times])

        video_interface_side = self.data_interface_objects["BehavioralVideoSide"]
        print(f"Setting aligned timestamps for video {video_interface_side.metadata_key_name}.")
        video_interface_side.set_aligned_timestamps(aligned_timestamps=[ttl_times])
