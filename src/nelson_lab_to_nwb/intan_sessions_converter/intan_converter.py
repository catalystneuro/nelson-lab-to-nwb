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

    # def temporally_align_data_interfaces(self):
    #     video_interface_top = self.data_interface_objects["BehavioralVideoTop"]
    #     video_interface_top.set_aligned_starting_time(ttl_times[0])

    #     video_interface_side = self.data_interface_objects["BehavioralVideoSide"]
    #     video_interface_side.set_aligned_starting_time(ttl_times[0])