from typing import Optional
from pynwb import NWBFile
from neuroconv import BaseDataInterface
from neuroconv.utils import FilePathType, FolderPathType
import pandas as pd
import tdt


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


class NoldusInterface(BaseDataInterface):
    """
    Custom data interface class for converting Noldus behavior data.
    """

    display_name = "Noldus Behavior Interface"
    associated_suffixes = ("csv", "xlsx")
    info = "Interface for Noldus behavioral data."

    def __init__(
        self,
        raw_behavior_path: Optional[FilePathType] = None,
        tdt_block_path: Optional[FolderPathType] = None,
        verbose: bool = False
    ):
        """
        Args:
            raw_behavior_path (FilePathType, optional): Path to the raw behavior data file. Defaults to None.
            tdt_block_path (FolderPathType, optional): Path to the TDT block file. Defaults to None.
            verbose (bool, optional): Whether to print verbose output. Defaults to False.
        """
        super().__init__(
            raw_behavior_path=raw_behavior_path,
            processed_behavior_path=processed_behavior_path,
            tdt_block_path=tdt_block_path,
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

        # # Processed behavior
        # self.processed_behavior_path = processed_behavior_path
        # if processed_behavior_path:
        #     self.processed_df = pd.read_excel(io=processed_behavior_path, engine='openpyxl')
        # else:
        #     self.processed_df = None

        # TDT block reader
        if tdt_block_path:
            self.reader = tdt.read_block(block_path=str(tdt_block_path))


    def add_to_nwbfile(
        self,
        nwbfile: NWBFile,
        metadata: Optional[dict] = dict(),
        timestamps_column_name: str = "Trial time",
        ttl_sync_epoc_name: str = "Cam2",
    ) -> None:

        ttl_sync_array = self.reader.epocs[ttl_sync_epoc_name].onset

