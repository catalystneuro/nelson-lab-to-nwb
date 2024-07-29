"""Primary script to run to convert sessions using the NWBConverter."""
from pathlib import Path
from neuroconv.utils import load_dict_from_file, dict_deep_update
from neuroconv.utils import FilePathType, FolderPathType


def session_to_nwb(
    *,
    output_folder_path: FolderPathType,
    tdt_folder_path: FolderPathType,
    noldus_file_path: FilePathType,
    aim_score_file_path: FilePathType,
    behavioral_video_file_path: FilePathType,
    user_metadata_file_path: FilePathType,
    noldus_variables_columns_names: list = ["Elongation", "Velocity", "Distance moved", "Rotation"],
    noldus_epoc_name: str = "Cam2",
    aim_epoc_name: str = "TTL1",
    overwrite: bool = False,
    verbose: bool = True,
):
    """Convert a session to NWB.

    Parameters
    ----------
    output_folder_path : FolderPathType
        Path to the output folder.
    tdt_folder_path : FolderPathType
        Path to the TDT data folder.
    noldus_file_path : FilePathType
        Path to the Noldus (.xlsx) file.
    aim_score_file_path : FilePathType
        Path to the AIMScore (.xlsx) file.
    behavioral_video_file_path : FilePathType
        Path to the behavioral video file (.mp4, .avi).
    user_metadata_file_path : FilePathType
        Path to the user metadata file (.yaml).
    noldus_variables_columns_names : list, optional (default ["Elongation", "Velocity", "Distance moved", "Rotation"])
        Names of the columns in the Noldus file that contain the variables of interest, by default ["Elongation", "Velocity", "Distance moved", "Rotation"].
    noldus_epoc_name : str, optional (default "Cam2")
        Name of the epoc in the TDT data that marks the start of the Noldus recording, by default "Cam2".
    aim_epoc_name : str, optional (default "TTL1")
        Name of the epoc in the TDT data that marks the start of the AIM score recording, by default "TTL1".
    overwrite : bool, optional (default False)
        Whether to overwrite the output NWB file, by default False.
    verbose : bool, optional (default True)
        Whether to print verbose output, by default True.
    """
    from nelson_lab_to_nwb.tdt_sessions_converter import TDTSessionConverter

    # Create output folder, if it doesn't exist
    output_folder = Path(output_folder_path)
    output_folder.mkdir(exist_ok=True)

    # Initialize converter
    source_data = dict(
        FiberPhotometry=dict(
            folder_path=tdt_folder_path,
            verbose=verbose,
        ),
        NoldusInterface=dict(
            file_path=noldus_file_path,
        ),
        AIMScore=dict(
            file_path=aim_score_file_path,
        ),
        BehavioralVideo=dict(
            file_paths=[behavioral_video_file_path],
        ),
    )

    converter = TDTSessionConverter(source_data=source_data, verbose=verbose)

    # Automatically fetch metadata from files, then update it with user-defined metadata
    source_metadata = converter.get_metadata()
    user_metadata_file = user_metadata_file_path
    user_metadata = load_dict_from_file(file_path=user_metadata_file)
    metadata = dict_deep_update(source_metadata, user_metadata)

    # Get events from the TDT data for synchronization
    tdt_events = converter.data_interface_objects.get("FiberPhotometry").get_events()
    aim_time_offset = tdt_events.get(aim_epoc_name).get("onset")[0]

    noldus_timestamps = tdt_events.get(noldus_epoc_name).get("onset")
    noldus_df = converter.data_interface_objects.get("NoldusInterface").get_dataframe()
    noldus_synced_timestamps = list(noldus_timestamps[-noldus_df.shape[0]:])

    # Conversion options
    conversion_options = dict(
        NoldusInterface=dict(
            variables_columns_names=noldus_variables_columns_names,
            timestamps_column_name="Trial time",
            synced_timestamps=noldus_synced_timestamps,
        ),
        AIMScore=dict(
            timestamps_column_name="Time (minutes relative to injection)",
            aims_column_name="AIMS",
            timestamp_offset=aim_time_offset,
        ),
    )

    subject_id = metadata.get("Subject").get("subject_id")
    start_datetime = metadata.get("NWBFile").get("session_start_time").replace(":", "").replace("-", "")[:-4]
    nwbfile_path = str(output_folder / f"{subject_id}_{start_datetime}.nwb")

    # Run conversion
    converter.run_conversion(
        metadata=metadata,
        nwbfile_path=nwbfile_path,
        overwrite=overwrite,
        conversion_options=conversion_options
    )

    print(f"Conversion complete. NWB file saved to: {nwbfile_path}")

    return nwbfile_path
