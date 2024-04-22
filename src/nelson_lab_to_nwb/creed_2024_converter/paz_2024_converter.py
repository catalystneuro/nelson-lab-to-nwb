from nelson_lab_to_nwb.interfaces.nex_interface import NeuroExplorerRecordingInterface
from nelson_lab_to_nwb.interfaces.noldus_interface import NoldusInterface
from neuroconv import NWBConverter


class Creed2024NWBConverter(NWBConverter):
    """Primary conversion class for Creed experimental data."""

    data_interface_classes = dict(
        NeuroExplorerRecordingInterface=NeuroExplorerRecordingInterface,
        NoldusInterface=NoldusInterface,
    )
