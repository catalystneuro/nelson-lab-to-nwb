"""Primary script to run to convert sessions using the NWBConverter."""
from pathlib import Path
from neuroconv.utils import load_dict_from_file, dict_deep_update
from neuroconv.utils import FilePathType, FolderPathType


def session_to_nwb(
    *,
    output_folder_path: FolderPathType,
    stub_test: bool = False,
    overwrite: bool = False,
    verbose: bool = True,
):
    """Convert a session to NWB.

    Parameters
    ----------

    """
    from nelson_lab_to_nwb.blackrock_sessions_converter import BlackrockNWBConverter

    # Create output folder, if it doesn't exist
    output_folder = Path(output_folder_path)
    output_folder.mkdir(exist_ok=True)

    # Initialize converter
    source_data = dict(
        BlackrockRaw=dict(
            file_path="/media/luiz/Seagate Basic/storage/catalystneuro/nelson_lab/Raw_BlackRock_withCognitiveEvents/BlackRock_raw_H0.2_071823001.ns6"
        ),
        BlackrockLFP=dict(
            file_path="/media/luiz/Seagate Basic/storage/catalystneuro/nelson_lab/Raw_BlackRock_withCognitiveEvents/BlackRock_raw_H0.2_071823001.ns2"
        ),
        BlackrockSorting=dict(
            file_path="/media/luiz/Seagate Basic/storage/catalystneuro/nelson_lab/Raw_BlackRock_withCognitiveEvents/BlackRock_raw_H0.2_071823001.nev",
            sampling_frequency=30000,
        ),
        BehavioralEvents=dict(
            file_path="/media/luiz/Seagate Basic/storage/catalystneuro/nelson_lab/Raw_BlackRock_withCognitiveEvents/CognitiveBehavioral_Raw_H0.2.CSV"
        )
    )

    converter = BlackrockNWBConverter(source_data=source_data, verbose=verbose)

    # Automatically fetch metadata from files, then update it with user-defined metadata
    source_metadata = converter.get_metadata()
    user_metadata_file = "/mnt/shared_storage/Github/nelson-lab-to-nwb/src/nelson_lab_to_nwb/blackrock_sessions_converter/metadata_example.yaml"
    user_metadata = load_dict_from_file(file_path=user_metadata_file)
    metadata = dict_deep_update(source_metadata, user_metadata)

    # Conversion options
    conversion_options = dict(
        BlackrockRaw=dict(
            stub_test=True,
        ),
        BlackrockLFP=dict(
            write_as="lfp"
        )
    )

    subject_id = metadata.get("Subject").get("subject_id")
    start_datetime = metadata.get("NWBFile").get("session_start_time").replace(":", "").replace("-", "")[:-4]
    nwbfile_path = str(output_folder / f"{subject_id}_{start_datetime}.nwb")

    # Run conversion
    converter.run_conversion(
        metadata=metadata,
        nwbfile_path="converted_blackrock.nwb",
        overwrite=True,
        conversion_options=conversion_options
    )

    return nwbfile_path
