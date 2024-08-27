from pathlib import Path
from typing import Optional
from datetime import timezone
import tdt
import yaml
from neuroconv import BaseDataInterface
from neuroconv.utils import DirectoryPath, FilePath, dict_deep_update
from pynwb import NWBFile
from ndx_photometry import (
    FibersTable,
    PhotodetectorsTable,
    ExcitationSourcesTable,
    FluorophoresTable,
    FiberPhotometryResponseSeries,
    FiberPhotometry
)


class TdtFiberPhotometryInterface(BaseDataInterface):

    display_name = "TDT Fiber Photometry"
    associated_suffixes = ("tbk", "tdx", "tev", "tin", "tnt", "tsq", "sev", "txt")
    info = "Interface for TDT Fiber Photometry data."

    def __init__(self, folder_path: DirectoryPath, metadata_path: Optional[FilePath] = None, verbose: bool = False):
        """
        Custom data interface class for converting TDT Fiber Photometry recordings.

        Args:
            folder_path (DirectoryPath): Folder path containing the TDT data files.
            metadata_path (FilePath, optional): Path to the metadata YAML file. Defaults to None.
            verbose (bool, optional): Whether to print verbose output. Defaults to False.
        """
        super().__init__(verbose=verbose, folder_path=folder_path)
        self.folder_path = Path(folder_path)
        self.reader = tdt.read_block(block_path=str(self.folder_path))
        if metadata_path:
            with open(str(metadata_path), "r") as f:
                self.extra_metadata = yaml.safe_load(f)
        else:
            self.extra_metadata = {}

    def get_metadata(self) -> dict:
        metadata = super().get_metadata()
        metadata["NWBFile"]["session_start_time"] = self.reader.info.start_date.replace(tzinfo=timezone.utc)
        metadata = dict_deep_update(metadata, self.extra_metadata)
        return metadata

    def add_to_nwbfile(
        self,
        nwbfile: NWBFile,
        metadata: Optional[dict] = dict(),
    ) -> None:
        fiber_photometry_metadata = metadata.get("Ophys", {}).get("FiberPhotometry", {})
        if not fiber_photometry_metadata:
            raise ValueError("Fiber Photometry metadata is missing from the metadata dictionary.")

        # Create a Fibers table, and add one (or many) fiber(s) to it
        fibers_table = FibersTable(description="fibers table")
        for f in fiber_photometry_metadata.get("Fibers", []):
            fibers_table.add_row(
                location=f.get("location", "location not defined"),
                notes=f.get("notes", "notes not defined"),
                coordinates=f.get("coordinates", None),
                fiber_model_number=f.get("fiber_model_number", "model number not defined"),
                dichroic_model_number=f.get("dichroic_model_number", "model number not defined"),
            )

        # Create an Excitation Sources table, and a one (or many) excitation source(s) to it
        excitationsources_table = ExcitationSourcesTable(description="excitation sources table")
        for e in fiber_photometry_metadata.get("ExcitationSources", []):
            excitationsources_table.add_row(
                peak_wavelength=e.get("peak_wavelength"),
                source_type=e.get("source_type", "source type not defined"),
            )

        # Create a Photodetectors table, and add one (or many) photodetector(s) to it
        photodetectors_table = PhotodetectorsTable(description="photodetectors table")
        for p in fiber_photometry_metadata.get("Photodetectors", []):
            photodetectors_table.add_row(
                peak_wavelength=p.get("peak_wavelength"),
                gain=p.get("gain"),
                type=p.get("type", "type not defined"),
                model_number=p.get("model_number", "model number not defined"),
            )

        # Create a Fluorophores table, and add one (or many) fluorophore(s) to it
        fluorophores_table = FluorophoresTable(description="fluorophores table")
        for f in fiber_photometry_metadata.get("Fluorophores", []):
            fluorophores_table.add_row(
                label=f.get("label", "label not defined"),
                location=f.get("location", "location not defined"),
                coordinates=f.get("coordinates", None),
                emission_peak_wavelength=f.get("emission_peak_wavelength"),
                excitation_peak_wavelength=f.get("excitation_peak_wavelength"),
            )

        # Add the metadata tables to the metadata section
        nwbfile.add_lab_meta_data(
            FiberPhotometry(
                fibers=fibers_table,
                excitation_sources=excitationsources_table,
                photodetectors=photodetectors_table,
                fluorophores=fluorophores_table
            )
        )

        # Create a raw FiberPhotometryResponseSeries, this is your main acquisition
        # We should create DynamicTableRegion referencing the correct rows for each table
        stream_names = list(self.reader.streams.keys())
        for stream in fiber_photometry_metadata.get("FiberPhotometryResponseSeries", []):
            stream_name = stream.get("name")
            if stream_name not in stream_names:
                raise ValueError(
                    f"Signal stream {stream_name} not found in TDT data.",
                    f"Available stream names: {stream_names}",
                )
            fiber_ref = fibers_table.create_fiber_region(
                region=stream.get("fibers", []),
                description='source fibers'
            )
            excitation_ref = excitationsources_table.create_excitation_source_region(
                region=stream.get("excitation_sources", []),
                description='excitation sources'
            )
            photodetector_ref = photodetectors_table.create_photodetector_region(
                region=stream.get("photodetectors", []),
                description='photodetectors'
            )
            fluorophore_ref = fluorophores_table.create_fluorophore_region(
                region=stream.get("fluorophores", []),
                description='fluorophores'
            )
            fp_response_series = FiberPhotometryResponseSeries(
                name=stream_name,
                data=self.reader.streams[stream_name].data,
                rate=self.reader.streams[stream_name].fs,
                unit=stream.get("unit", "F"),
                fibers=fiber_ref,
                excitation_sources=excitation_ref,
                photodetectors=photodetector_ref,
                fluorophores=fluorophore_ref,
            )
            nwbfile.add_acquisition(nwbdata=fp_response_series)
