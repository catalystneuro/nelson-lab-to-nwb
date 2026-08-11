from typing import Dict, Literal

from nelson_lab_to_nwb.interfaces import (
    NeuroExplorerRecordingInterface,
    NoldusInterface,
    AIMScoreInterface,
)
from nelson_lab_to_nwb.utils.probe import set_probe
from neuroconv import NWBConverter


class PlexonNWBConverter(NWBConverter):
    """Primary conversion class for Plexon sessions data, pre-converted to Neuroexplorer format (.nex)."""

    data_interface_classes = dict(
        NeuroExplorerRecordingInterface=NeuroExplorerRecordingInterface,
        NoldusInterface=NoldusInterface,
        AIMScore=AIMScoreInterface,
    )

    def __init__(
        self,
        source_data: Dict[str, dict],
        probe_type: Literal["type_1", "type_2"] = "type_1",
        verbose: bool = True,
    ):
        super().__init__(source_data=source_data, verbose=verbose)

        # Add probe information: https://probeinterface.readthedocs.io/en/main/index.html
        nex_interface = self.data_interface_objects["NeuroExplorerRecordingInterface"]
        set_probe(nex_interface.recording_extractor, probe_type=probe_type)
