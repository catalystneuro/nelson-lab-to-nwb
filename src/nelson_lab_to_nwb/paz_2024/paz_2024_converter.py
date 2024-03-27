from nelson_lab_to_nwb.interfaces.tdt_interface import TdtFiberPhotometryInterface
from nelson_lab_to_nwb.interfaces.noldus_interface import NoldusInterface
from neuroconv import NWBConverter


class Paz2024NWBConverter(NWBConverter):
    """Primary conversion class for Paz experimental data."""

    data_interface_classes = dict(
        TdtFiberPhotometryInterface=TdtFiberPhotometryInterface,
        NoldusInterface=NoldusInterface,
    )
