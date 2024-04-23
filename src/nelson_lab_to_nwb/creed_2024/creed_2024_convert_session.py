"""Primary script to run to convert sessions using the NWBConverter."""
from pathlib import Path
from neuroconv.utils import load_dict_from_file, dict_deep_update
from neuroconv.utils import FilePathType, FolderPathType

from nelson_lab_to_nwb.creed_2024 import Creed2024NWBConverter


def session_to_nwb(
    *,
    nex_file_path: FilePathType,
    noldus_file_path: FilePathType,
    aim_score_file_path: FilePathType,
    metadata_file_path: FilePathType,
    output_folder_path: FolderPathType,
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

    # Run conversion
    conversion_options = dict(
        NeuroExplorerRecordingInterface=dict(
            stub_test=stub_test
        ),
        NoldusInterface=dict(
            variables_columns_names=["Elongation", "Velocity", "Distance moved", "Rotation"],
            timestamps_column_name="Trial time",
        ),
        AIMScore=dict(
            timestamps_column_name="Time (minutes relative to injection)",
            aims_column_name="AIMS",
            # reference_timestamps=
        )
    )

    subject_id = metadata.get("Subject").get("subject_id")
    start_datetime = metadata.get("session_start_time").replace(":", "").replace("-", "")[:-4]
    nwbfile_path = str(output_folder / f"{subject_id}_{start_datetime}.nwb")

    converter.run_conversion(
        metadata=metadata,
        nwbfile_path=nwbfile_path,
        conversion_options=conversion_options,
        overwrite=overwrite
    )
