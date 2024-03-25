from nelson_lab_to_nwb.interfaces.tdt_interface import TdtFiberPhotometryInterface
from neuroconv import NWBConverter


class Azcorra2023NWBConverter(NWBConverter):
    """Primary conversion class for Paz experimental data."""

    data_interface_classes = dict(
        TdtFiberPhotometryInterface=TdtFiberPhotometryInterface,
        # Events=PicoscopeEventInterface,
    )