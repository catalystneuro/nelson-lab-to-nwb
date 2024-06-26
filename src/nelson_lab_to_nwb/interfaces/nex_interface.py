from typing import Optional, Literal
from neuroconv.datainterfaces.ecephys.baserecordingextractorinterface import BaseRecordingExtractorInterface
from neuroconv.utils import FilePathType
from pynwb import NWBFile
import numpy as np


class NeuroExplorerRecordingInterface(BaseRecordingExtractorInterface):
    """
    Primary data interface class for converting NeuroExplorer data using the

    :py:class:`~spikeinterface.extractors.neoextractors.neuroexplorer.NeuroExplorerRecordingExtractor`.
    """

    display_name = "NeuroExplorer Recording"
    associated_suffixes = (".nex", )
    info = "Interface for NeuroExplorer recording data."

    def __init__(
        self,
        file_path: FilePathType,
        es_key: str = "ElectricalSeries",
        verbose: bool = True,
    ):
        from spikeinterface.extractors.neoextractors.neuroexplorer import NeuroExplorerRecordingExtractor
        from spikeinterface.core import aggregate_channels

        self.Extractor = NeuroExplorerRecordingExtractor
        streams_names = NeuroExplorerRecordingExtractor.get_streams(file_path=file_path)[0]

        # Because this recorder only extracts one channel at a time, we need to aggregate the channels
        recording_list = [NeuroExplorerRecordingExtractor(file_path=file_path, stream_name=stream_name) for stream_name in streams_names]
        self.recording_extractor = aggregate_channels(recording_list)

        self.neo_rec0 = recording_list[0].neo_reader
        self.recording_header = self.neo_rec0.header

        self.subset_channels = None
        self.verbose = verbose
        self.es_key = es_key
        self._number_of_segments = self.recording_extractor.get_num_segments()

    def add_to_nwbfile(
        self,
        nwbfile: NWBFile,
        metadata: Optional[dict] = dict(),
        stub_test: bool = False,
        starting_time: Optional[float] = None,
        write_as: Literal["raw", "lfp", "processed"] = "raw",
        write_electrical_series: bool = True,
        compression: Optional[str] = "gzip",
        compression_opts: Optional[int] = None,
        iterator_type: str = "v2",
        iterator_opts: Optional[dict] = None,
        include_units: bool = True,
        units_suffix_ignore: list[str] = ["_wf", "_template"],
    ) -> None:
        super().add_to_nwbfile(
            nwbfile=nwbfile,
            metadata=metadata,
            stub_test=stub_test,
            starting_time=starting_time,
            write_as=write_as,
            write_electrical_series=write_electrical_series,
            compression=compression,
            compression_opts=compression_opts,
            iterator_type=iterator_type,
            iterator_opts=iterator_opts,
        )
        if include_units:
            units_data = dict()
            spike_channels = self.recording_header['spike_channels']
            spike_channels_ind_dict = {sc[0]: ii for ii, sc in enumerate(spike_channels)}
            for ii, sc in enumerate(spike_channels):
                if not any([suffix in sc[0] for suffix in units_suffix_ignore]):
                    units_data = dict(
                        spike_times=self.neo_rec0.get_spike_timestamps(spike_channel_index=ii),
                        waveform_mean=None,
                    )
                    if sc[0] + "_template" in spike_channels_ind_dict:
                        sc_ind = spike_channels_ind_dict[sc[0] + "_template"]
                        units_data["waveform_mean"] = np.squeeze(self.neo_rec0.get_spike_raw_waveforms(spike_channel_index=sc_ind))
                    nwbfile.add_unit(**units_data)
