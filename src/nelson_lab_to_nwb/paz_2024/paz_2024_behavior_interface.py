from typing import Optional
from pynwb import NWBFile
from neuroconv import BaseDataInterface
from neuroconv.utils import FilePathType
import pandas as pd


def find_header_row(file_path, header_names: list = ["Trial time", "Recording time"]):
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


class Paz2024BehaviorInterface(BaseDataInterface):
    """
    Custom data interface class for converting Paz behavior data.
    """

    display_name = "Paz Behavior Interface"
    associated_suffixes = ("csv", "xlsx")
    info = "Interface for behavioral data."

    def __init__(
        self,
        raw_behavior_path: Optional[FilePathType] = None,
        processed_behavior_path: Optional[FilePathType] = None,
        verbose: bool = False
    ):
        """
        Args:
            raw_behavior_path (FilePathType, optional): Path to the raw behavior data file. Defaults to None.
            processed_behavior_path (FilePathType, optional): Path to the processed behavior data file. Defaults to None.
            verbose (bool, optional): Whether to print verbose output. Defaults to False.
        """
        super().__init__(
            raw_behavior_path=raw_behavior_path,
            processed_behavior_path=processed_behavior_path,
            verbose=verbose
        )

        # Raw behavior
        self.raw_behavior_path = raw_behavior_path
        if raw_behavior_path:
            header_row = find_header_row(raw_behavior_path, header_names=["Trial time", "Recording time"])
            if header_row is not None:
                df = pd.read_excel(
                    io=str(raw_behavior_path),
                    header=header_row,
                    engine='openpyxl'
                )
                self.raw_df = df.drop(index=0)
            else:
                raise ValueError("Could not find the header row in the raw behavior file.")
        else:
            self.raw_df = None

        # Processed behavior
        self.processed_behavior_path = processed_behavior_path
        if processed_behavior_path:
            self.processed_df = pd.read_excel(io=processed_behavior_path, engine='openpyxl')
        else:
            self.processed_df = None

    def add_to_nwbfile(
        self,
        nwbfile: NWBFile,
        metadata: Optional[dict] = dict(),
    ) -> None:
        pass
