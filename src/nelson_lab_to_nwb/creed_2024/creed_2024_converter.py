from nelson_lab_to_nwb.interfaces import (
    NeuroExplorerRecordingInterface,
    NoldusInterface,
    AIMScoreInterface
)
from neuroconv import NWBConverter


class Creed2024NWBConverter(NWBConverter):
    """Primary conversion class for Creed experimental data."""

    data_interface_classes = dict(
        NeuroExplorerRecordingInterface=NeuroExplorerRecordingInterface,
        NoldusInterface=NoldusInterface,
        AIMScore=AIMScoreInterface
    )
