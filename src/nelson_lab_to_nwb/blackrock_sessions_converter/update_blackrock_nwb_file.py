"""
Updates NWB files generated for Blackrock sessions:
- Removes Units table
- Adds SpikeEventSeries for each unsorted array of spike events (one per channel)
"""
from pynwb import NWBHDF5IO
from pynwb.ecephys import SpikeEventSeries
from neo.rawio import BlackrockRawIO


def update_nwb_file(
    nwb_file_path: str,
    nev_file_path: str,
):
    """
    Update the NWB file by removing the Units table and adding SpikeEventSeries for each unsorted array of spike events.

    Parameters
    ----------
    nwb_file_path : str
        Path to the NWB file to be updated.
    nev_file_path : str
        Path to the Blackrock .nev file containing the spike events.
    """
    out_file_path = nwb_file_path.replace(".nwb", "_updated.nwb")

    # Load the Blackrock file
    neo_reader = BlackrockRawIO(
        filename=nev_file_path,
        nsx_to_load=[],
        load_nev=True,
    )
    neo_reader.parse_header()

    conversion_scale_dict = {
        "V": 1.,
        "mV": 1e-3,
        "uV": 1e-6,
    }

    with NWBHDF5IO(nwb_file_path, mode="r") as in_io:
        nwbfile = in_io.read()
        if nwbfile.units is not None:
            # Unlink the Units table from its parent container, NWBFile
            nwbfile.units.reset_parent()
            # remove the Units table from the NWBFile fields
            # this is a temporary hack to get around the fact that nwbfile.units is a special attribute of NWBFile
            nwbfile.fields["units"] = None

        # Stores unsorted spike events
        spike_channels = neo_reader.header["spike_channels"]
        for ind, spk_ch in enumerate(spike_channels):
            name = spk_ch["name"]
            el_ind = int(name.split("ch")[-1].split("#")[0]) - 1
            el_region = nwbfile.create_electrode_table_region(
                region=[el_ind],
                description=f"electrode_{el_ind}",
            )
            wf_unit = spk_ch["wf_units"]
            conversion_scale = conversion_scale_dict.get(wf_unit, 1.)

            spike_events = SpikeEventSeries(
                name=f"SpikeEvents_Electrode_{el_ind}",
                description="Events detected with threshold crossing, manually set for each electrode.",
                data=neo_reader.get_spike_raw_waveforms(spike_channel_index=ind),
                timestamps=neo_reader.get_spike_timestamps(spike_channel_index=ind),
                electrodes=el_region,
                conversion=spk_ch["wf_gain"] * conversion_scale,
            )
            nwbfile.add_acquisition(spike_events)

        # Write a new file that contains everything *except* Units
        with NWBHDF5IO(out_file_path, mode="w") as out_io:
            out_io.export(src_io=in_io, nwbfile=nwbfile)

        print(f"Updated NWB file saved to {out_file_path}.")