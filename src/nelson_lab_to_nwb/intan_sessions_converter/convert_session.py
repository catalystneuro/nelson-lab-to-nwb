"""Primary script to run to convert sessions using the NWBConverter."""
from pathlib import Path
from pydantic import FilePath, DirectoryPath

from neuroconv.utils import load_dict_from_file, dict_deep_update


def session_to_nwb(
    *,
    output_folder_path: DirectoryPath,
    intan_folder_path: FilePath,
    aim_score_file_path: FilePath,
    top_behavioral_video_file_path: FilePath,
    side_behavioral_video_file_path: FilePath,
    user_metadata_file_path: FilePath,
    injection_time_in_seconds: float = 0.0,
    stub_test: bool = False,
    overwrite: bool = False,
    verbose: bool = True,
):
    """Convert a session to NWB.

    Parameters
    ----------
    output_folder_path : DirectoryPath
        Path to the output folder.
    intan_folder_path : FilePath
        Path to the Intan folder containing the .rhd data files.
    aim_score_file_path : FilePath
        Path to the AIM score file (.csv, .xlsx).
    top_behavioral_video_file_path : FilePath
        Path to the top recording behavioral video file (.mp4, .avi).
    side_behavioral_video_file_path : FilePath
        Path to the side recording behavioral video file (.mp4, .avi).
    user_metadata_file_path : FilePath
        Path to the user metadata file (.yaml).
    injection_time_in_seconds : float, optional (default 0.0)
        Time of injection in seconds, used to synchronize AIM scores. Default 0.0.
    stub_test : bool, optional (default False)
        Whether to run the conversion in stub test mode, by default False.
    overwrite : bool, optional (default False)
        Whether to overwrite the output NWB file, by default False.
    verbose : bool, optional (default True)
        Whether to print verbose output, by default True.
    """
    from nelson_lab_to_nwb.intan_sessions_converter import IntanSessionNWBConverter

    # Create output folder, if it doesn't exist
    output_folder = Path(output_folder_path)
    output_folder.mkdir(exist_ok=True)

    # Initialize converter
    source_data = dict(
        IntanMultifilesRaw=dict(
            folder_path=intan_folder_path,
            verbose=verbose,
            es_key="ElectricalSeries",
        ),
        AIMScore=dict(
            file_path=aim_score_file_path,
            verbose=verbose
        ),
        BehavioralVideoTop=dict(
            file_paths=[top_behavioral_video_file_path],
            metadata_key_name="VideoTop",
            verbose=verbose
        ),
        BehavioralVideoSide=dict(
            file_paths=[side_behavioral_video_file_path],
            metadata_key_name="VideoSide",
            verbose=verbose
        ),
    )

    converter = IntanSessionNWBConverter(source_data=source_data, verbose=verbose)

    # Automatically fetch metadata from files, then update it with user-defined metadata
    source_metadata = converter.get_metadata()
    user_metadata_file = user_metadata_file_path
    user_metadata = load_dict_from_file(file_path=user_metadata_file)
    metadata = dict_deep_update(source_metadata, user_metadata)

    # Conversion options
    conversion_options = dict(
        AIMScore=dict(
            timestamps_column_name="Time (minutes relative to injection)",
            aims_column_name="AIMS",
            timestamp_offset=injection_time_in_seconds,
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
