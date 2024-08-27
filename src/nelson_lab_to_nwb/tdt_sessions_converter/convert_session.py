"""Primary script to run to convert sessions using the NWBConverter."""
from pathlib import Path
import numpy as np
from neuroconv.utils import load_dict_from_file, dict_deep_update
from pydantic import FilePath, DirectoryPath
from neuroconv.datainterfaces.behavior.video.video_utils import VideoCaptureContext


def get_video_synced_timestamps(video_path, camera_timestamps):
    with VideoCaptureContext(file_path=str(video_path)) as video:
        n_frames = video.frame_count
    n_missing_frames = n_frames - len(camera_timestamps)
    time_interval = np.mean(np.diff(camera_timestamps))
    starting_time = camera_timestamps[0]
    missing_timestamps = [starting_time - (i + 1) * time_interval for i in range(n_missing_frames)]
    video_synced_timestamps = missing_timestamps[::-1] + camera_timestamps
    return video_synced_timestamps


def session_to_nwb(
    *,
    output_folder_path: DirectoryPath,
    tdt_folder_path: DirectoryPath,
    noldus_file_path: FilePath,
    aim_score_file_path: FilePath,
    behavioral_video_file_path: FilePath,
    user_metadata_file_path: FilePath,
    noldus_variables_columns_names: list = ["Elongation", "Velocity", "Distance moved", "Rotation"],
    noldus_epoc_name: str = "Cam2",
    aim_epoc_name: str = "TTL1",
    overwrite: bool = False,
    verbose: bool = True,
):
    """Convert a session to NWB.

    Parameters
    ----------
    output_folder_path : DirectoryPath
        Path to the output folder.
    tdt_folder_path : DirectoryPath
        Path to the TDT data folder.
    noldus_file_path : FilePath
        Path to the Noldus (.xlsx) file.
    aim_score_file_path : FilePath
        Path to the AIMScore (.xlsx) file.
    behavioral_video_file_path : FilePath
        Path to the behavioral video file (.mp4, .avi).
    user_metadata_file_path : FilePath
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

    camera_ttl_timestamps = tdt_events.get(noldus_epoc_name).get("onset")
    noldus_df = converter.data_interface_objects.get("NoldusInterface").get_dataframe()
    noldus_synced_timestamps = list(camera_ttl_timestamps[-noldus_df.shape[0]:])

    # Because the TDT acquisition system misses the TTL times for the first video frames,
    # we need to manually add the first N timestamps to the camera synced timestamps list
    # where N = n_frames - n_ttls
    video_synced_timestamps = get_video_synced_timestamps(
        video_path=behavioral_video_file_path,
        camera_timestamps=list(camera_ttl_timestamps),
    )
    video_interface_top = converter.data_interface_objects["BehavioralVideo"]
    video_interface_top.set_aligned_timestamps(aligned_timestamps=[video_synced_timestamps])

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
    start_datetime = metadata.get("NWBFile").get("session_start_time").replace(":", "").replace("-", "")[:15]
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
