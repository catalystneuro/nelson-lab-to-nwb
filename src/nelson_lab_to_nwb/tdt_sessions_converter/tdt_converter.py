from neuroconv import NWBConverter
from neuroconv.datainterfaces import TDTFiberPhotometryInterface, VideoInterface
from nelson_lab_to_nwb.interfaces import NoldusInterface, AIMScoreInterface


class TDTSessionConverter(NWBConverter):
    """Primary conversion class for TDT recording sessions data."""

    data_interface_classes = dict(
        FiberPhotometry=TDTFiberPhotometryInterface,
        AIMScore=AIMScoreInterface,
        NoldusInterface=NoldusInterface,
        BehavioralVideo=VideoInterface,
    )
