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
        BehavioralVideo=VideoInterface,
    )
