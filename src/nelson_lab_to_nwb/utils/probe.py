from typing import Literal
from probeinterface import Probe
import numpy as np


# The geometry of the 32-channel optrode array, kept here because it is the only description of
# that probe anyone wrote down. It is not attached to the recording: the array has no channel map
# on record, so which of these positions belongs to which recording channel is unknown, and an
# unverified assignment writes a wrong coordinate for every electrode. Attach it once the lab
# supplies the wiring.
OPTRODE_ARRAY_POSITIONS = np.array(
    [[450, 0], [600, 0]]
    + [[150, 150], [300, 150], [450, 150], [600, 150], [750, 150], [900, 150]]
    + [[0, 300], [150, 300], [300, 300], [450, 300], [600, 300], [750, 300], [900, 300], [1050, 300]]
    + [[0, 450], [150, 450], [300, 450], [750, 450], [900, 450], [1050, 450]]
    + [[0, 600], [150, 600], [300, 600], [750, 600], [900, 600], [1050, 600]]
    + [[150, 750], [300, 750], [750, 750], [900, 750]]
)

# Intan channel at each contact of the 64-channel probe, read off `P64-8 Mapping.pdf`, page 104 of
# the 2019 Diagnostic Biochips catalogue, headed "ASSY INT64" and "Recording sites mapped to Intan
# system". Each list runs from the tip of the shank towards its base. The sheet draws shank 1 front
# view and shank 2 back view, so the two columns of shank 2 may be mirrored with respect to those
# of shank 1, which would exchange their x coordinates by 22.5 um and change nothing else.
P64_8_SHANK_1_LEFT = [17, 21, 25, 29, 30, 26, 13, 15, 14, 12, 10, 8, 6, 4, 2, 0]
P64_8_SHANK_1_RIGHT = [19, 23, 27, 31, 28, 24, 22, 20, 18, 16, 1, 3, 5, 7, 9, 11]
P64_8_SHANK_2_LEFT = [62, 58, 54, 50, 49, 53, 34, 32, 33, 35, 37, 39, 41, 43, 45, 47]
P64_8_SHANK_2_RIGHT = [60, 56, 52, 48, 51, 55, 57, 59, 61, 63, 46, 44, 42, 40, 38, 36]


def set_probe_type_1(extractor) -> None:
    probe = Probe(
        ndim=2,
        si_units="um",
        name="32-Channel Optrode Array",
        manufacturer="Innovative Neurophysiology",
    )
    probe.set_contacts(
        positions=np.full((32, 2), np.nan),
        shapes="circle",
        shape_params={"radius": 4},
        contact_ids=np.arange(0, 32),
        shank_ids=np.zeros(32),
    )
    probe.set_device_channel_indices(channel_indices=np.arange(0, 32))
    extractor.set_probe(probe, in_place=True)


def set_probe_type_2(extractor) -> None:
    # Two shanks 250 um apart, each of two columns of 16 contacts at a 25 um vertical pitch, with
    # the second column offset by 22.5 um across and 12.5 um up.
    columns = [
        (P64_8_SHANK_1_LEFT, 0.0, 0.0, 0),
        (P64_8_SHANK_1_RIGHT, 22.5, 12.5, 0),
        (P64_8_SHANK_2_LEFT, 250.0, 0.0, 1),
        (P64_8_SHANK_2_RIGHT, 272.5, 12.5, 1),
    ]
    positions = []
    device_channel_indices = []
    shank_ids = []
    for channels, x, y_offset, shank_id in columns:
        for position_in_column, channel in enumerate(channels):
            positions.append([x, position_in_column * 25 + y_offset])
            device_channel_indices.append(channel)
            shank_ids.append(shank_id)

    probe = Probe(
        ndim=2,
        si_units="um",
        name="P64-8",
        manufacturer="Diagnostic Biochips",
    )
    probe.set_contacts(
        positions=np.array(positions),
        shapes="rect",
        shape_params={"width": 11, "height": 15},
        contact_ids=np.arange(0, 64),
        shank_ids=np.array(shank_ids),
    )
    probe.set_device_channel_indices(channel_indices=np.array(device_channel_indices))

    extractor.set_probe(probe, in_place=True)


def set_probe(
    extractor,
    probe_type: Literal["type_1", "type_2"] = "type_1",
) -> None:
    """
    Set the probe for the given extractor.

    Parameters
    ----------
    extractor : object
        The extractor object to set the probe for.
    probe_type : str
        The type of probe to set. Can be "type_1" or "type_2".
    """
    if probe_type == "type_1":
        set_probe_type_1(extractor)
    elif probe_type == "type_2":
        set_probe_type_2(extractor)
    else:
        raise ValueError(f"Unknown probe type: {probe_type}")
