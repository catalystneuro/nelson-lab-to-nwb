from typing import Optional, Literal
import yaml
from neuroconv.datainterfaces.ecephys.baserecordingextractorinterface import BaseRecordingExtractorInterface
from neuroconv.utils import FilePathType, dict_deep_update
from pynwb import NWBFile


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
        metadata_path: Optional[FilePathType] = None,
        es_key: str = "ElectricalSeries",
        verbose: bool = True,
    ):
        from spikeinterface.extractors.neoextractors.neuroexplorer import NeuroExplorerRecordingExtractor
        from spikeinterface.core import aggregate_channels

        self.Extractor = NeuroExplorerRecordingExtractor
        streams_names = NeuroExplorerRecordingExtractor.get_streams(file_path=file_path)[0]
        recording_list = [NeuroExplorerRecordingExtractor(file_path=file_path, stream_name=stream_name) for stream_name in streams_names]
        self.recording_extractor = aggregate_channels(recording_list)
        self.subset_channels = None
        self.verbose = verbose
        self.es_key = es_key
        self._number_of_segments = self.recording_extractor.get_num_segments()
        if metadata_path:
            with open(str(metadata_path), "r") as f:
                self.extra_metadata = yaml.safe_load(f)
        else:
            self.extra_metadata = {}

    def get_metadata(self) -> dict:
        metadata = super().get_metadata()
        metadata = dict_deep_update(metadata, self.extra_metadata)
        return metadata

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
