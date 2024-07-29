from typing import Optional, Union
from pynwb import NWBFile, TimeSeries
from neuroconv import BaseDataInterface
from neuroconv.utils import FilePathType
import pandas as pd
import numpy as np


def find_header_row(file_path, header_names: list) -> Optional[int]:
    """
    Find the header row in an Excel file containing specific keywords.
    """
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


def expand_aims_to_seconds(
    df: pd.DataFrame,
    timestamps_column_name: str,
    aims_column_name: str,
    timestamp_offset: float = 0.0
):
    """
    Expand the AIMS score data to seconds.

    Args:
        df (pd.DataFrame): DataFrame containing the AIMS score data.
        timestamps_column_name (str): Name of the column containing the timestamps.
        aims_column_name (str): Name of the column containing the AIMS scores.
        timestamp_offset (float, optional): Offset to add to the timestamps. Defaults to 0.0.

    Returns:
        tuple: Expanded time array and expanded AIMS score
    """
    times = df[timestamps_column_name].values * 60 + timestamp_offset
    values = df[aims_column_name].values

    # Find the range of the expanded time array
    min_time = times[0]
    max_time = times[-1]

    # Create the expanded arrays
    expanded_times = np.arange(min_time, max_time + 1)
    expanded_values = np.zeros_like(expanded_times)

    # Fill the expanded values array
    value_idx = 0
    for i, t in enumerate(expanded_times):
        if value_idx < len(times) - 1 and t >= times[value_idx + 1]:
            value_idx += 1
        expanded_values[i] = values[value_idx]

    return (expanded_times, expanded_values)


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

    def get_dataframe(
        self,
        timestamps_column_name: str = "Time (minutes relative to injection)",
        aims_column_name: str = "AIMS"
    ) -> pd.DataFrame:
        """
        Read the AIM score behavior data file into a DataFrame.

        Returns:
            pd.DataFrame: DataFrame containing the AIM score behavior data.
        """
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
            if df[aims_column_name].isna().any():
                print(f"There are NaN values in the {aims_column_name} column. Forward filling these values.")
                df[aims_column_name] = df[aims_column_name].ffill()
            return df
        else:
            raise ValueError("Could not find the header row in the AIM score behavior file.")

    def add_to_nwbfile(
        self,
        nwbfile: NWBFile,
        metadata: Optional[dict] = dict(),
        timestamps_column_name: str = "Time (minutes relative to injection)",
        aims_column_name: str = "AIMS",
        timestamp_offset: float = 0.0
    ) -> None:
        # Read file into DataFrame
        df = self.get_dataframe(
            timestamps_column_name=timestamps_column_name,
            aims_column_name=aims_column_name
        )

        # Expand AIMS scores from minutes to seconds
        expanded_times, expanded_values = expand_aims_to_seconds(
            df=df,
            timestamps_column_name=timestamps_column_name,
            aims_column_name=aims_column_name,
            timestamp_offset=timestamp_offset,
        )

        # Create processing module and add TimeSeries
        if "behavior" not in nwbfile.processing:
            behavior_module = nwbfile.create_processing_module(
                name="behavior", description="Processed behavioral data"
            )
        else:
            behavior_module = nwbfile.processing["behavior"]

        aims_ts = TimeSeries(
            name="aims",
            data=expanded_values,
            unit="na",
            timestamps=expanded_times,
        )
        behavior_module.add(aims_ts)
