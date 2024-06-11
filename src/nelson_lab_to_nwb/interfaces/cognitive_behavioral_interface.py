from pynwb import NWBFile
from ndx_events import LabeledEvents
from neuroconv import BaseDataInterface
from neuroconv.utils import FilePathType
import pandas as pd


class CognitiveBehavioralInterface(BaseDataInterface):
    """
    Custom data interface class for converting CognitiveBehavioral_Raw data.
    """

    display_name = "Cognitive Behavioral data Interface"
    associated_suffixes = ("csv", "xlsx")
    info = "Interface for CognitiveBehavioral_Raw data."

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

    def add_to_nwbfile(
        self,
        nwbfile: NWBFile,
        metadata: dict,
        events_column_name: str = "Event Name",
        events_times_column_name: str = "Event Time",
        behavioral_events_time_offset: int = 0
    ) -> None:
        df = pd.read_csv(filepath_or_buffer=self.file_path)

        # Strip spaces from column names
        df.columns = df.columns.str.strip()

        # Get events names and factorize them
        df[events_column_name] = df[events_column_name].str.replace(r'\s+', ' ', regex=True).str.strip()
        df["Event Name Factorized"], unique_event_names = pd.factorize(df[events_column_name])

        # Convert timestamps to datetime
        df["Date"] = pd.to_datetime(df["Date"], format="%Y/%m/%d %H:%M")

        # Convert timedelta to total seconds
        df[events_times_column_name] = df[events_times_column_name].str.replace(r'(\d+:\d+:\d+):(\d+)', r'\1.\2', regex=True)
        df[events_times_column_name] = pd.to_timedelta(df[events_times_column_name])
        df[events_times_column_name] = df[events_times_column_name].dt.total_seconds()

        # Apply time offset
        t0 = pd.Timestamp(metadata["NWBFile"]["session_start_time"])
        t1 = df["Date"][0]
        offset = pd.Timedelta(seconds=behavioral_events_time_offset * 3600)
        offset_in_seconds = (t1 + offset - t0).total_seconds()

        # create a new LabeledEvents type to hold behavioral events
        events = LabeledEvents(
            name='CognitiveBehavioral_Raw',
            description='Cognitive behavioral raw events.',
            timestamps=df["Event Time"].values + offset_in_seconds,
            data=df["Event Name Factorized"].values,
            labels=list(unique_event_names)
        )
        nwbfile.add_acquisition(events)
