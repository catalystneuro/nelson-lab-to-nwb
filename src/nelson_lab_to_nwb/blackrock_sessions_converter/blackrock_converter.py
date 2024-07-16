from typing import Dict
from neuroconv.datainterfaces import BlackrockRecordingInterface, BlackrockSortingInterface, VideoInterface
from nelson_lab_to_nwb.interfaces import CognitiveBehavioralInterface
from neuroconv import NWBConverter

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

        # Align video timestamps
