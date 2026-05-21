from typing import Literal
from probeinterface import Probe, generate_multi_shank
import numpy as np


def set_probe_type_1(extractor) -> None:
    positions = [[450, 0], [600, 0]]
    positions.extend([[150, 150], [300, 150], [450, 150], [600, 150], [750, 150], [900, 150]])
    positions.extend(
        [
            [0, 300],
            [150, 300],
            [300, 300],
            [450, 300],
            [600, 300],
            [750, 300],
            [900, 300],
            [1050, 300],
        ]
    )
    positions.extend([[0, 450], [150, 450], [300, 450], [750, 450], [900, 450], [1050, 450]])
    positions.extend([[0, 600], [150, 600], [300, 600], [750, 600], [900, 600], [1050, 600]])
    positions.extend([[150, 750], [300, 750], [750, 750], [900, 750]])
    positions = np.array(positions)

    probe = Probe(
        ndim=2,
        si_units="um",
        name="32-Channel Optrode Array",
        manufacturer="Innovative Neurophysiology",
    )
    probe.set_contacts(
        positions=positions,
        shapes="circle",
        shape_params={"radius": 4},
        contact_ids=np.arange(0, 32),
        shank_ids=np.zeros(32),
    )
    probe.set_device_channel_indices(channel_indices=np.arange(0, 32))
    extractor.set_probe(probe, in_place=True)


def set_probe_type_2(extractor) -> None:
    probe = generate_multi_shank(
        num_shank=2,
        num_columns=2,
        num_contact_per_column=16,
        shank_pitch=[250., 0],
    )

    positions = np.zeros((64, 2))
    for i in range(0, 16):
        positions[i] = (0, i * 25)
    for i in range(16, 32):
        positions[i] = (22.5, (i-16) * 25 + 12.5)
    for i in range(32, 48):
        positions[i] = (250, (i-32) * 25)
    for i in range(48, 64):
        positions[i] = (275.5, (i-48) * 25 + 12.5)

    probe.set_contacts(
        positions=positions,
        shapes="rect",
        shape_params={"width": 11, "height": 15},
        contact_ids=np.arange(0, 64),
    )

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
