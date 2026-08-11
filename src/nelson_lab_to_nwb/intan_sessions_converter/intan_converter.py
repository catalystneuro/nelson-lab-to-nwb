from nelson_lab_to_nwb.interfaces import (
    IntanMultifilesRecordingInterface,
    AIMScoreInterface,
)
from neuroconv import NWBConverter
from neuroconv.datainterfaces import ExternalVideoInterface


class IntanSessionNWBConverter(NWBConverter):
    """Primary conversion class for Intan recording + behavioral data."""

    data_interface_classes = dict(
        IntanMultifilesRaw=IntanMultifilesRecordingInterface,
        AIMScore=AIMScoreInterface,
        BehavioralVideoTop=ExternalVideoInterface,
        BehavioralVideoSide=ExternalVideoInterface,
    )

    def temporally_align_data_interfaces(self, metadata: dict | None = None, conversion_options: dict | None = None):
        # Extract TTL times from Intan data and set aligned timestamps for video data
        intan_interface = self.data_interface_objects["IntanMultifilesRaw"]
        ttl_times = intan_interface.extract_ttl_times()

        for interface_name in ("BehavioralVideoTop", "BehavioralVideoSide"):
            video_interface = self.data_interface_objects.get(interface_name, None)
            if video_interface is None:
                continue
            print(f"Setting aligned timestamps for video {video_interface.video_name}.")
            video_interface.set_aligned_timestamps(aligned_timestamps=[ttl_times])
