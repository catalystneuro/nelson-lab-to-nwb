from neuroconv.datainterfaces import BlackrockRecordingInterface, BlackrockSortingInterface, VideoInterface
from nelson_lab_to_nwb.interfaces import CognitiveBehavioralInterface
from neuroconv import NWBConverter


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
