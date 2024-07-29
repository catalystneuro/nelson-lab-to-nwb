from neuroconv import NWBConverter
from neuroconv.datainterfaces import TDTFiberPhotometryInterface, VideoInterface
from nelson_lab_to_nwb.interfaces import NoldusInterface, AIMScoreInterface


class TDTSessionConverter(NWBConverter):
    """Primary conversion class for Paz experimental data."""

    data_interface_classes = dict(
        FiberPhotometry=TDTFiberPhotometryInterface,
        NoldusInterface=NoldusInterface,
        AIMScore=AIMScoreInterface,
        BehavioralVideo=VideoInterface,
    )

    # def temporally_align_data_interfaces(self):
    #     # Align video timestamps