# DANDI archive instructions

## Setup

1. Create a DANDI account at https://dandiarchive.org/

2. Install the DANDI client in your local Python environment (already gets installed in the conda environment of this repo):
```
pip install dandi
```

3. Export your DANDI API token as an environment variable (copy it from DANDI archive website):
```
export DANDI_API_KEY=personal-key-value
```

## Upload data

Given that you have a DANDI dataset created, you can upload data to it using the DANDI client.

1. Download the dataset to a local directory:
```
dandi download https://dandiarchive.org/dandiset/<dataset_id>/draft
```

2. Change directory to the dataset folder:
```
cd <dataset_id>
```

3. Organize the converted NWB files according to the DANDI dataset structure, where `<source_folder>` is the folder containing the NWB files created by your conversion script:
```
dandi organize <source_folder> --media-files-mode copy --update-external-file-paths
```

4. Run validation on the dataset:
```
dandi validate .
```

5. Upload the dataset to the DANDI archive:
```
dandi upload
```


Reference: https://www.dandiarchive.org/handbook/13_upload/