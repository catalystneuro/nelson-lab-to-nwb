from neuroconv.datainterfaces import BlackrockRecordingInterface, BlackrockSortingInterface
from nelson_lab_to_nwb.interfaces import CognitiveBehavioralInterface
from neuroconv import NWBConverter


class BlackrockNWBConverter(NWBConverter):
    """Primary conversion class for Blackrock recording + sorting experimental data."""

    data_interface_classes = dict(
        BlackrockRaw=BlackrockRecordingInterface,
        BlackrockLFP=BlackrockRecordingInterface,
        BlackrockSorting=BlackrockSortingInterface,
        BehavioralEvents=CognitiveBehavioralInterface
    )
