from typing import Optional, Literal
from neuroconv.datainterfaces.ecephys.baserecordingextractorinterface import BaseRecordingExtractorInterface
from neuroconv.utils import FilePathType
from pynwb import NWBFile
from pynwb.ogen import OptogeneticSeries
import numpy as np

from nelson_lab_to_nwb.utils.probe import set_probe


def reconstruct_ttl_signal(rise_timestamps, step_duration, amplitudes, reconstruction_sampling_rate=1000):
    total_time = rise_timestamps[-1] + step_duration + 1.
    num_samples = int(total_time * reconstruction_sampling_rate)  # Convert total_time (seconds) to samples
    time_vector = np.linspace(0, total_time, num_samples)
    ttl_signal = np.zeros(num_samples)
    for i, rise_time in enumerate(rise_timestamps):
        start_sample = int(rise_time * reconstruction_sampling_rate)
        end_sample = start_sample + int(step_duration * reconstruction_sampling_rate)
        ttl_signal[start_sample:end_sample] = amplitudes[i]
    return time_vector, ttl_signal


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
        channels_to_remove: list = ["Laser", "AD50"],
        verbose: bool = True,
    ):
        from spikeinterface.extractors.neoextractors.neuroexplorer import NeuroExplorerRecordingExtractor
        from spikeinterface.core import aggregate_channels

        self.Extractor = NeuroExplorerRecordingExtractor
        streams_names = NeuroExplorerRecordingExtractor.get_streams(file_path=file_path)[0]

        # Because this recorder only extracts one channel at a time, we need to aggregate the channels
        recording_list = [
            NeuroExplorerRecordingExtractor(file_path=file_path, stream_name=stream_name)
            for stream_name in streams_names
        ]
        self.recording_extractor = aggregate_channels(recording_list)

        # Remove extra channels: "Laser" and "AD50"
        ids_to_remove = list()
        for i in self.recording_extractor.channel_ids:
            name = self.recording_extractor.get_channel_property(channel_id=i, key="channel_name")
            if name in channels_to_remove:
                ids_to_remove.append(i)
        self.recording_extractor = self.recording_extractor.remove_channels(remove_channel_ids=ids_to_remove)

        # Add probe information: https://probeinterface.readthedocs.io/en/main/index.html
        set_probe(self.recording_extractor)

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
        units_suffix_ignore: list = ["_wf", "_template"],
        ogen_event_name: str = "Laser",
        ogen_ttl_samplig_rate: float = 40000.,
        ogen_amplitudes_array: list = [],
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
        # Units
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

        # Optogenetic stimulus
        ogen_event_id = None
        for ev in self.neo_rec0.header.get("event_channels", []):
            if ev[0] == ogen_event_name:
                ogen_event_id = int(ev[1])

        if ogen_event_id is None:
            print(f"Optogenetic event with name {ogen_event_name} was not found.")
        else:
            # Add OptogeneticSeries
            ogen_metadata = metadata.get("Ogen", dict())
            device = nwbfile.create_device(**ogen_metadata.get("Device", dict()))
            site_metadata = ogen_metadata.get("StimulusSite", dict())
            site_metadata["device"] = device
            ogen_site = nwbfile.create_ogen_site(**site_metadata)
            ogen_timestamps = self.neo_rec0.get_event_timestamps(event_channel_index=ogen_event_id)[0] / ogen_ttl_samplig_rate
            if not ogen_amplitudes_array:
                ogen_amplitudes_array = np.array([0.5] * 1000 + [1.] * 1000 + [2.] * 1000 + [4.] * 1000) * 0.001
            ttl_times, ttl_signal = reconstruct_ttl_signal(
                rise_timestamps=ogen_timestamps,
                step_duration=0.15,
                amplitudes=ogen_amplitudes_array,
            )
            ogen_series = OptogeneticSeries(
                name="OptogeneticSeries",
                data=ttl_signal,
                site=ogen_site,
                timestamps=ttl_times,
            )
            nwbfile.add_stimulus(ogen_series)

            # Add Optogenetics stimulation as trials
            nwbfile.add_trial_column(
                name="stimulus_amplitude",
                description="Amplitude of the optogenetic stimulus",
            )
            for i, start_time in enumerate(ogen_timestamps):
                nwbfile.add_trial(
                    start_time=start_time,
                    stop_time=start_time + 0.15,
                    stimulus_amplitude=ogen_amplitudes_array[i],
                )
