"""Primary script to run to convert sessions using the NWBConverter."""
from pathlib import Path
from neuroconv.utils import load_dict_from_file, dict_deep_update
from neuroconv.utils import FilePathType, FolderPathType


def session_to_nwb(
    *,
    nex_file_path: FilePathType,
    noldus_file_path: FilePathType,
    aim_score_file_path: FilePathType,
    metadata_file_path: FilePathType,
    output_folder_path: FolderPathType,
    noldus_start_event_name: str = "Noldus Start",
    stub_test: bool = False,
    overwrite: bool = False,
    verbose: bool = True,
):
    """Convert a session to NWB.

    Parameters
    ----------
    nex_file_path : FilePathType
        Path to the NeuroExplorer (.nex) file.
    noldus_file_path : FilePathType
        Path to the Noldus (.xlsx) file.
    aim_score_file_path : FilePathType
        Path to the AIMScore (.xlsx) file.
    metadata_file_path : FilePathType
        Path to the metadata (.json) file.
    output_folder_path : FolderPathType
        Path to the output folder.
    stub_test : bool, optional (default False)
        Whether to run the conversion in stub test mode, by default False.
    overwrite : bool, optional (default False)
        Whether to overwrite the output NWB file, by default False.
    verbose : bool, optional (default True)
        Whether to print verbose output, by default True.
    """
    from nelson_lab_to_nwb.creed_2024 import Creed2024NWBConverter

    # Create output folder, if it doesn't exist
    output_folder = Path(output_folder_path)
    output_folder.mkdir(exist_ok=True)

    # Initialize converter
    source_data = dict(
        NeuroExplorerRecordingInterface=dict(
            file_path=nex_file_path
        ),
        NoldusInterface=dict(
            file_path=noldus_file_path
        ),
        AIMScore=dict(
            file_path=aim_score_file_path
        )
    )
    converter = Creed2024NWBConverter(source_data=source_data, verbose=verbose)

    # Load and update metadata
    converter_metadata = converter.get_metadata()
    extra_metadata = load_dict_from_file(metadata_file_path)
    metadata = dict_deep_update(converter_metadata, extra_metadata)

    # Get Noldus event time from nex file
    nex_interface = converter.data_interface_objects["NeuroExplorerRecordingInterface"]
    neo_rec = nex_interface.neo_rec0
    noldus_time_offset = None
    for ii, ev in enumerate(nex_interface.recording_header.get("event_channels", [])):
        if ev[0] == noldus_start_event_name:
            noldus_time_offset = neo_rec.rescale_event_timestamp(
                event_timestamps=neo_rec.get_event_timestamps(event_channel_index=int(ev[1]))[0][0]
            )
            # noldus_time_offset = ev[1]
            break
    if noldus_time_offset is None:
        Warning(f"Could not find event '{noldus_start_event_name}' in the NeuroExplorer file. Setting to noldus_time_offset=0.")
        noldus_time_offset = 0.0

    # Run conversion
    conversion_options = dict(
        NeuroExplorerRecordingInterface=dict(
            stub_test=stub_test
        ),
        NoldusInterface=dict(
            variables_columns_names=["Elongation", "Velocity", "Distance moved", "Rotation"],
            timestamps_column_name="Trial time",
            timestamp_offset=noldus_time_offset
        ),
        AIMScore=dict(
            timestamps_column_name="Time (minutes relative to injection)",
            aims_column_name="AIMS",
            # reference_timestamps=
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
