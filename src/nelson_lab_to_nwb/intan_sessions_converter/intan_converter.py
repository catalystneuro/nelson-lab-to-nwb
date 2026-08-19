from typing import Dict, Literal

from nelson_lab_to_nwb.interfaces import AIMScoreInterface
from nelson_lab_to_nwb.utils.probe import set_probe
from neuroconv import NWBConverter
from neuroconv.datainterfaces import ExternalVideoInterface, IntanDigitalInterface, IntanRecordingInterface


class IntanSessionNWBConverter(NWBConverter):
    """Primary conversion class for Intan recording + behavioral data."""

    data_interface_classes = dict(
        IntanRecording=IntanRecordingInterface,
        IntanDigital=IntanDigitalInterface,
        AIMScore=AIMScoreInterface,
        BehavioralVideoTop=ExternalVideoInterface,
        BehavioralVideoSide=ExternalVideoInterface,
    )

    def __init__(
        self,
        source_data: Dict[str, dict],
        probe_type: Literal["type_1", "type_2"] = "type_1",
        verbose: bool = True,
    ):
        super().__init__(source_data=source_data, verbose=verbose)

        # Add probe information: https://probeinterface.readthedocs.io/en/main/index.html
        recording_interface = self.data_interface_objects["IntanRecording"]
        set_probe(recording_interface.recording_extractor, probe_type=probe_type)

    def temporally_align_data_interfaces(self, metadata: dict | None = None, conversion_options: dict | None = None):
        # The camera emits one pulse per frame on DIGITAL-IN-14, so the video timestamps are its rising edges
        video_interface_names = [
            name for name in ("BehavioralVideoTop", "BehavioralVideoSide") if name in self.data_interface_objects
        ]
        if not video_interface_names:
            return

        digital_interface = self.data_interface_objects.get("IntanDigital", None)
        if digital_interface is None:
            raise ValueError(
                "This session carries no digital lines, so there is nothing to take the video timestamps from. "
                "Convert it without the video arguments, or pass a session recorded with DIGITAL-IN-14 enabled."
            )
        ttl_times = digital_interface.get_event_times(event_type_source_id="DIGITAL-IN-14")

        for interface_name in video_interface_names:
            video_interface = self.data_interface_objects[interface_name]
            print(f"Setting aligned timestamps for video {video_interface.metadata_key}.")
            video_interface.set_aligned_timestamps(aligned_timestamps=[ttl_times])
