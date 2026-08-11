from typing import Dict, Literal

from nelson_lab_to_nwb.interfaces import AIMScoreInterface, extract_ttl_times
from nelson_lab_to_nwb.utils.probe import set_probe
from neuroconv import NWBConverter
from neuroconv.datainterfaces import ExternalVideoInterface, IntanRecordingInterface


class IntanSessionNWBConverter(NWBConverter):
    """Primary conversion class for Intan recording + behavioral data."""

    data_interface_classes = dict(
        IntanMultifilesRaw=IntanRecordingInterface,
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
        intan_interface = self.data_interface_objects["IntanMultifilesRaw"]
        set_probe(intan_interface.recording_extractor, probe_type=probe_type)
        self.intan_folder_path = intan_interface.source_data["file_path"].parent

    def temporally_align_data_interfaces(self, metadata: dict | None = None, conversion_options: dict | None = None):
        # Extract TTL times from Intan data and set aligned timestamps for video data
        ttl_times = extract_ttl_times(folder_path=self.intan_folder_path)

        for interface_name in ("BehavioralVideoTop", "BehavioralVideoSide"):
            video_interface = self.data_interface_objects.get(interface_name, None)
            if video_interface is None:
                continue
            print(f"Setting aligned timestamps for video {video_interface.metadata_key}.")
            video_interface.set_aligned_timestamps(aligned_timestamps=[ttl_times])
