from typing import Optional, Union
from pynwb import NWBFile
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
        reference_timestamps: Union[list[float], np.ndarray, None] = None,
        variables_names: list[str] = ["Elongation", "Velocity", "Distance moved", "Rotation"],
        verbose: bool = False
    ):
        """
        Args:
            file_path (FilePathType): Path to the behavior data file.
            reference_timestamps (Union[list[float], np.ndarray], optional): Reference timestamps for synchronization. Defaults to None.
            verbose (bool, optional): Whether to print verbose output. Defaults to False.
        """
        super().__init__(
            file_path=file_path,
            verbose=verbose
        )

        # Raw behavior
        self.file_path = file_path
        header_row = find_header_row(file_path, header_names=["Trial time", "Recording time"])
        if header_row is not None:
            df = pd.read_excel(
                io=str(file_path),
                header=header_row,
                engine='openpyxl'
            )
            df = df.drop(index=0)
            self.df = df[[*variables_names, "Trial time"]]
        else:
            raise ValueError("Could not find the header row in the raw behavior file.")

        timestamp_samples = self.df["Trial time"].astype(float) / 0.05
        self.df["timestamp_samples"] = timestamp_samples

        if reference_timestamps is not None:
            self.df["synced_timestamps"] = [
                reference_timestamps[int(t)]
                if int(t) < len(reference_timestamps)
                else None
                for t in timestamp_samples
            ]

        # # Processed behavior
        # self.processed_behavior_path = processed_behavior_path
        # if processed_behavior_path:
        #     self.processed_df = pd.read_excel(io=processed_behavior_path, engine='openpyxl')
        # else:
        #     self.processed_df = None

    def add_to_nwbfile(
        self,
        nwbfile: NWBFile,
        metadata: Optional[dict] = dict(),
        timestamps_column_name: str = "Trial time",
        ttl_sync_epoc_name: str = "Cam2",
    ) -> None:
        pass
