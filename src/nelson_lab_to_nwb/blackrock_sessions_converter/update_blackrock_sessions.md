# Update a Blackrock session

For unsorted spiking events, the original converter wrongly stored the spiking events in the `Units` table.
This is fixed by the code in `update_blackrock_nwb_file.py`, which removes the `Units` table and stores the spiking events as `SpikeEventSeries` instead.

After running a conversion, e.g.: (you can skip this step if you have already converted your session to NWB)
```python
from nelson_lab_to_nwb.blackrock_sessions_converter import session_to_nwb

session_to_nwb(
    output_folder_path="output_blackrock",
    blackrock_raw_file_path="path_to/BlackRock_raw_H0.2_071823001.ns6",
    blackrock_lfp_file_path="path_to/BlackRock_raw_H0.2_071823001.ns2",
    blackrock_sorting_file_path="path_to/BlackRock_raw_H0.2_071823001.nev",
    behavioral_events_file_path="path_to/CognitiveBehavioral_Raw_H0.2.CSV",
    behavioral_video_file_path="path_to/BlackRock_exampleVideo_H0.2.avi",
    user_metadata_file_path="path_to/metadata_example.yaml",
    behavioral_events_time_offset=5,
    stub_test=False,
    overwrite=True,
    verbose=True,
)
```

You can run the following code to update the NWB file:
```python
from nelson_lab_to_nwb.blackrock_sessions_converter.update_blackrock_nwb_file import update_nwb_file

update_nwb_file(
    nwb_file_path="path_to/converted.nwb",
    nev_file_path="path_to/BlackRock_raw_H0.2_071823001.nev",
)
```

