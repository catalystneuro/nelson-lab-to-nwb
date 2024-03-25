from nelson_lab_to_nwb.interfaces.tdt_interface import TdtFiberPhotometryInterface
from nelson_lab_to_nwb.paz_2024.paz_2024_behavior_interface import Paz2024BehaviorInterface
from neuroconv import NWBConverter


class Paz2024NWBConverter(NWBConverter):
    """Primary conversion class for Paz experimental data."""

    data_interface_classes = dict(
        TdtFiberPhotometryInterface=TdtFiberPhotometryInterface,
        BehaviorInterface=Paz2024BehaviorInterface,
    )