from nelson_lab_to_nwb.interfaces import (
    NeuroExplorerRecordingInterface,
    NoldusInterface,
    AIMScoreInterface
)
from neuroconv import NWBConverter


class PlexonNWBConverter(NWBConverter):
    """Primary conversion class for Plexon sessions data, pre-converted to Neuroexplorer format (.nex)."""

    data_interface_classes = dict(
        NeuroExplorerRecordingInterface=NeuroExplorerRecordingInterface,
        NoldusInterface=NoldusInterface,
        AIMScore=AIMScoreInterface,
    )
