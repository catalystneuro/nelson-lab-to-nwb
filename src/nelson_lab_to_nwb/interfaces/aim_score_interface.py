from typing import Optional, Union
from pynwb import NWBFile, TimeSeries
from neuroconv import BaseDataInterface
from neuroconv.utils import FilePathType
import pandas as pd
import numpy as np


def find_header_row(file_path, header_names: list) -> Optional[int]:
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


class AIMScoreInterface(BaseDataInterface):
    """
    Custom data interface class for converting AIM score behavior data.
    """

    display_name = "AIM Score Behavior Interface"
    associated_suffixes = ("csv", "xlsx")
    info = "Interface for AIM Score behavioral data."

    def __init__(
        self,
        file_path: FilePathType,
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
        self.file_path = file_path

    def add_to_nwbfile(
        self,
        nwbfile: NWBFile,
        metadata: Optional[dict] = dict(),
        timestamps_column_name: str = "Time (minutes relative to injection)",
        aims_column_name: str = "AIMS",
        reference_timestamps: Union[list[float], np.ndarray, None] = None,
        timestamp_offset: float = 0.0
    ) -> None:
        # Read file into DataFrame
        header_row = find_header_row(
            file_path=self.file_path,
            header_names=[timestamps_column_name, aims_column_name]
        )
        if header_row is not None:
            df = pd.read_excel(
                io=str(self.file_path),
                header=header_row,
                engine='openpyxl'
            )
            df = df[[timestamps_column_name, aims_column_name]]
        else:
            raise ValueError("Could not find the header row in the AIM score behavior file.")

        # Create processing module and add TimeSeries
        if "behavior" not in nwbfile.processing:
            behavior_module = nwbfile.create_processing_module(
                name="behavior", description="Processed behavioral data"
            )
        else:
            behavior_module = nwbfile.processing["behavior"]
        data = df[aims_column_name].values
        timestamps = df[timestamps_column_name].values * 60 + timestamp_offset
        aims_ts = TimeSeries(
            name="aims",
            data=data,
            unit="na",
            timestamps=timestamps
        )
        behavior_module.add(aims_ts)
