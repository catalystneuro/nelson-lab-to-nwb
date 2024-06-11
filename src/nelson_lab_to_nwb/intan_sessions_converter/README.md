# Raw_Intan_Ephys_withVideos

- Raw electrophysiology traces as multiple `.rhd`
- AIM score behavioral data `.xlsx`
- Behavioral video as `.avi`


## Usage

```python
from nelson_lab_to_nwb.intan_sessions_converter import session_to_nwb

session_to_nwb(
    output_folder_path="/path_to_output_folder/",

    user_metadata_file_path="/path_to/session_metadata.yaml",
    stub_test=False,
    overwrite=False,
    verbose=True,
)
```