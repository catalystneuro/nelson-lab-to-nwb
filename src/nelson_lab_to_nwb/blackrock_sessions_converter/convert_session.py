"""Primary script to run to convert sessions using the NWBConverter."""
from pathlib import Path
from neuroconv.utils import load_dict_from_file, dict_deep_update
from neuroconv.utils import FilePathType, FolderPathType


def session_to_nwb(
    *,
    output_folder_path: FolderPathType,
    blackrock_raw_file_path: FilePathType,
    blackrock_lfp_file_path: FilePathType,
    blackrock_sorting_file_path: FilePathType,
    behavioral_events_file_path: FilePathType,
    behavioral_video_file_path: FilePathType,
    user_metadata_file_path: FilePathType,
    behavioral_events_time_offset: int = 0,
    stub_test: bool = False,
    overwrite: bool = False,
    verbose: bool = True,
):
    """Convert a session to NWB.

    Parameters
    ----------
    output_folder_path : FolderPathType
        Path to the output folder.
    blackrock_raw_file_path : FilePathType
        Path to the Blackrock raw data file (.ns6).
    blackrock_lfp_file_path : FilePathType
        Path to the Blackrock LFP data file (.ns2).
    blackrock_sorting_file_path : FilePathType
        Path to the Blackrock sorting data file (.nev).
    behavioral_events_file_path : FilePathType
        Path to the behavioral events file (.csv).
    behavioral_video_file_path : FilePathType
        Path to the behavioral video file (.mp4, .avi).
    user_metadata_file_path : FilePathType
        Path to the user metadata file (.yaml).
    behavioral_events_time_offset : int, optional (default 0)
        Time offset, in hours, to apply to behavioral events, by default 0.
    stub_test : bool, optional (default False)
        Whether to run the conversion in stub test mode, by default False.
    overwrite : bool, optional (default False)
        Whether to overwrite the output NWB file, by default False.
    verbose : bool, optional (default True)
        Whether to print verbose output, by default True.
    """
    from nelson_lab_to_nwb.blackrock_sessions_converter import BlackrockNWBConverter

    # Create output folder, if it doesn't exist
    output_folder = Path(output_folder_path)
    output_folder.mkdir(exist_ok=True)

    # Initialize converter
    source_data = dict(
        BlackrockRaw=dict(
            file_path=blackrock_raw_file_path,
            verbose=verbose
        ),
        BlackrockLFP=dict(
            file_path=blackrock_lfp_file_path,
            verbose=verbose
        ),
        BlackrockSorting=dict(
            file_path=blackrock_sorting_file_path,
            sampling_frequency=30000,
            verbose=verbose
        ),
        BehavioralEvents=dict(
            file_path=behavioral_events_file_path,
            verbose=verbose
        ),
        BehavioralVideo=dict(
            file_paths=[behavioral_video_file_path],
        ),
    )

    converter = BlackrockNWBConverter(source_data=source_data, verbose=verbose)

    # Automatically fetch metadata from files, then update it with user-defined metadata
    source_metadata = converter.get_metadata()
    user_metadata_file = user_metadata_file_path
    user_metadata = load_dict_from_file(file_path=user_metadata_file)
    metadata = dict_deep_update(source_metadata, user_metadata)

    # Conversion options
    conversion_options = dict(
        BlackrockRaw=dict(
            stub_test=stub_test,
        ),
        BlackrockLFP=dict(
            write_as="lfp",
            stub_test=stub_test,
        ),
        BehavioralEvents=dict(
            events_column_name="Event Name",
            events_times_column_name="Event Time",
            behavioral_events_time_offset=behavioral_events_time_offset,
        )
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
