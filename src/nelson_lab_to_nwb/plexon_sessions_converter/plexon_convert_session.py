"""Primary script to run to convert sessions using the NWBConverter."""
from pathlib import Path
from typing import Optional
from neuroconv.utils import load_dict_from_file, dict_deep_update
from neuroconv.utils import FilePathType, FolderPathType


def session_to_nwb(
    *,
    output_folder_path: FolderPathType,
    nex_file_path: FilePathType,
    noldus_file_path: FilePathType,
    aim_score_file_path: FilePathType,
    metadata_file_path: FilePathType,
    channel_names_to_remove: list = ["Laser", "AD50"],
    noldus_start_event_name: str = "Noldus Start",
    noldus_variables_columns_names: list = ["Elongation", "Velocity", "Distance moved", "Rotation"],
    aim_start_event_name: str = "Keyboard1",
    include_units: bool = True,
    ogen_event_name: str = "Laser",
    ogen_amplitudes_array: list = [],
    stub_test: Optional[bool] = False,
    overwrite: Optional[bool] = False,
    verbose: Optional[bool] = True,
):
    """Convert a session to NWB.

    Parameters
    ----------
    output_folder_path : FolderPathType
        Path to the output folder.
    nex_file_path : FilePathType
        Path to the NeuroExplorer (.nex) file.
    noldus_file_path : FilePathType
        Path to the Noldus (.xlsx) file.
    aim_score_file_path : FilePathType
        Path to the AIMScore (.xlsx) file.
    metadata_file_path : FilePathType
        Path to the metadata (.json) file.
    channel_names_to_remove : list, optional (default ["Laser", "AD50"])
        Names of the channels to remove from the NeuroExplorer file, by default ["Laser", "AD50"].
    noldus_start_event_name : str, optional (default "Noldus Start")
        Name of the event in the NeuroExplorer file that marks the start of the Noldus recording, by default "Noldus Start".
    noldus_variables_columns_names : list, optional (default ["Elongation", "Velocity", "Distance moved", "Rotation"])
        Names of the columns in the Noldus file that contain the variables of interest, by default ["Elongation", "Velocity", "Distance moved", "Rotation"].
    aim_start_event_name : str, optional (default "Keyboard1")
        Name of the event in the NeuroExplorer file that marks the start of the AIMScore recording, by default "Keyboard1".
    include_units : bool, optional (default True)
        Whether to include units from .nex file in the output NWB file, by default True.
    ogen_event_name : str, optional (default "Laser")
        Name of the event channel in the NeuroExplorer file containing the Optogenetics stimulation signal, by default "Laser".
    ogen_amplitudes_array : list, optional (default [])
        Array of amplitudes (in Watts) for the Optogenetics stimulation signal.
        If not explicitly provided, the amplitudes used will be:
        1-1000: 0.5 mW, 1001-2000: 1 mW, 2001-3000: 2 mW, 3001-4000: 4 mW.
    stub_test : bool, optional (default False)
        Whether to run the conversion in stub test mode, by default False.
    overwrite : bool, optional (default False)
        Whether to overwrite the output NWB file, by default False.
    verbose : bool, optional (default True)
        Whether to print verbose output, by default True.
    """
    from nelson_lab_to_nwb.plexon_sessions_converter import PlexonNWBConverter

    # Create output folder, if it doesn't exist
    output_folder = Path(output_folder_path)
    output_folder.mkdir(exist_ok=True)

    # Initialize converter
    source_data = dict(
        NeuroExplorerRecordingInterface=dict(
            file_path=nex_file_path,
            channels_to_remove=channel_names_to_remove
        ),
        NoldusInterface=dict(
            file_path=noldus_file_path
        ),
        AIMScore=dict(
            file_path=aim_score_file_path
        )
    )
    converter = PlexonNWBConverter(source_data=source_data, verbose=verbose)

    # Load and update metadata
    converter_metadata = converter.get_metadata()
    extra_metadata = load_dict_from_file(metadata_file_path)
    metadata = dict_deep_update(converter_metadata, extra_metadata)

    # Get Noldus event time from nex file
    nex_interface = converter.data_interface_objects["NeuroExplorerRecordingInterface"]
    neo_rec = nex_interface.neo_rec0
    noldus_time_offset = None
    aim_time_offset = None
    for ii, ev in enumerate(nex_interface.recording_header.get("event_channels", [])):
        if ev[0] == noldus_start_event_name:
            noldus_time_offset = neo_rec.rescale_event_timestamp(
                event_timestamps=neo_rec.get_event_timestamps(event_channel_index=int(ev[1]))[0][0]
            )
            print(f"Found event '{noldus_start_event_name}' at time {noldus_time_offset}.")
        if ev[0] == aim_start_event_name:
            aim_time_offset = neo_rec.rescale_event_timestamp(
                event_timestamps=neo_rec.get_event_timestamps(event_channel_index=int(ev[1]))[0][0]
            )
            print(f"Found event '{aim_start_event_name}' at time {aim_time_offset}.")
    if noldus_time_offset is None:
        Warning(f"Could not find event '{noldus_start_event_name}' in the NeuroExplorer file. Setting to noldus_time_offset=0.")
        noldus_time_offset = 0.0
    if aim_time_offset is None:
        Warning(f"Could not find event '{aim_start_event_name}' in the NeuroExplorer file. Setting to aim_time_offset=0.")
        aim_time_offset = 0.0

    # Run conversion
    conversion_options = dict(
        NeuroExplorerRecordingInterface=dict(
            write_as="lfp",
            stub_test=stub_test,
            include_units=include_units,
            units_suffix_ignore=["_wf", "_template"],
            ogen_event_name=ogen_event_name,
            ogen_ttl_samplig_rate=40000.,
            ogen_amplitudes_array=ogen_amplitudes_array,
        ),
        NoldusInterface=dict(
            variables_columns_names=noldus_variables_columns_names,
            timestamps_column_name="Trial time",
            timestamp_offset=noldus_time_offset
        ),
        AIMScore=dict(
            timestamps_column_name="Time (minutes relative to injection)",
            aims_column_name="AIMS",
            timestamp_offset=aim_time_offset
        )
    )

    subject_id = metadata.get("Subject").get("subject_id")
    start_datetime = metadata.get("NWBFile").get("session_start_time").replace(":", "").replace("-", "")[:-4]
    nwbfile_path = str(output_folder / f"{subject_id}_{start_datetime}.nwb")

    converter.run_conversion(
        metadata=metadata,
        nwbfile_path=nwbfile_path,
        conversion_options=conversion_options,
        overwrite=overwrite
    )

    return nwbfile_path
