# Raw_BlackRock_withCognitiveEvents

- Spike data as `.nev `
- Raw electrophysiology traces as `.ns6`
- LFP traces as `.ns2`
- Behavioral events as `.csv`
- Behavioral video as `.avi`


## Usage

```python
from nelson_lab_to_nwb.blackrock_sessions_converter import session_to_nwb

session_to_nwb(
    output_folder_path="/path_to_output_folder/",
    blackrock_raw_file_path="/path_to/raw_blackrock_file.ns6",
    blackrock_lfp_file_path="/path_to/lfp_blackrock_file.ns2",
    blackrock_sorting_file_path="/path_to/sorting_blackrock_file.nev",
    behavioral_events_file_path="/path_to/behavioral_events.csv",
    behavioral_video_file_path="/path_to/behavioral_video.avi",
    user_metadata_file_path="/path_to/session_metadata.yaml",
    behavioral_events_time_offset=5,
    stub_test=False,
    overwrite=False,
    verbose=True,
)
```