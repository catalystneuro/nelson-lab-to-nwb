# Raw_Plexon_ephys_LIDpaper

- Processed electrophysiology traces (LFP) from `.nex`
- Putative Unites from `.nex`
- AIM score behavioral data from `.xlsx`
- Noldus behavioral data from `.xlsx`
- Time sync for AIM and Noldus from `.nex`


## Usage

```python
from nelson_lab_to_nwb.plexon_sessions_converter import session_to_nwb

output_file_path = session_to_nwb(
    output_folder_path="converted_session",
    nex_file_path="/path_to/file.nex",
    noldus_file_path="/path_to/file.xlsx",
    aim_score_file_path="/path_to/file.xlsx",
    metadata_file_path="/path_to/metadata.yaml",
    include_units=True,
    stub_test=False,
    overwrite=True,
    verbose=True,
)
```