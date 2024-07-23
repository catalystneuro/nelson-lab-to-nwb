from typing import Optional
from pynwb import NWBFile, TimeSeries
from neuroconv import BaseDataInterface
from neuroconv.utils import FilePathType
import pandas as pd
import numpy as np


def find_header_row(file_path, header_names: list = ["Trial time", "Recording time"]) -> Optional[int]:
    with pd.ExcelFile(file_path, engine='openpyxl') as xls:
        # Loop through each row in the first sheet
        for sheet_name in xls.sheet_names:
            sheet = xls.parse(sheet_name=sheet_name, header=None)
            for row_idx, row in sheet.iterrows():
                # Check for a specific pattern or keywords in the row
                if all([name in row.values for name in header_names]):
                    return row_idx
    # Return None if no header is found
    return None


class NoldusInterface(BaseDataInterface):
    """
    Custom data interface class for converting Noldus behavior data.
    """

    display_name = "Noldus Behavior Interface"
    associated_suffixes = ("csv", "xlsx")
    info = "Interface for Noldus behavioral data."

    def __init__(
        self,
        file_path: FilePathType,
        verbose: bool = False
    ):
        """
        Args:
            file_path (FilePathType): Path to the behavior data file.
            verbose (bool, optional): Whether to print verbose output. Defaults to False.
        """
        super().__init__(
            file_path=file_path,
            verbose=verbose
        )
        self.file_path = file_path
        header_row = find_header_row(file_path, header_names=["Trial time", "Recording time"])
        if header_row is not None:
            df = pd.read_excel(
                io=str(file_path),
                header=header_row,
                engine='openpyxl'
            )
            self.df = df.drop(index=0)
        else:
            raise ValueError("Could not find the header row in the raw behavior file.")

    def add_to_nwbfile(
        self,
        nwbfile: NWBFile,
        metadata: Optional[dict] = dict(),
        variables_columns_names: list = ["Elongation", "Velocity", "Distance moved", "Rotation"],
        timestamps_column_name: str = "Trial time",
        reference_timestamps: list = None,
        timestamp_offset: float = 0.0
    ) -> None:

        self.df = self.df[variables_columns_names + [timestamps_column_name]]
        timestamp_samples = self.df[timestamps_column_name].astype(float) / 0.05
        self.df["timestamp_samples"] = timestamp_samples

        if reference_timestamps is not None:
            self.df["synced_timestamps"] = [
                reference_timestamps[int(t)]
                if int(t) < len(reference_timestamps)
                else None
                for t in timestamp_samples
            ]
        else:
            self.df["synced_timestamps"] = self.df[timestamps_column_name].astype(float) + timestamp_offset

        # Create processing module and add TimeSeries
        if "behavior" not in nwbfile.processing:
            behavior_module = nwbfile.create_processing_module(
                name="behavior", description="Processed behavioral data"
            )
        else:
            behavior_module = nwbfile.processing["behavior"]
        timestamps = self.df["synced_timestamps"].values
        for var_name in variables_columns_names:
            # self.df[var_name] = self.df[var_name].replace('-', 0).infer_objects()
            self.df[var_name] = self.df[var_name].replace('-', 0)
            self.df[var_name] = self.df[var_name].infer_objects(copy=False)
            data = self.df[var_name].values
            ts = TimeSeries(
                name=var_name,
                data=data,
                unit="na",
                timestamps=timestamps
            )
            behavior_module.add(ts)
