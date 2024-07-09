from probeinterface import Probe
import numpy as np


def set_probe(extractor):
    positions = [[450, 0], [600, 0]]
    positions.extend([[150, 150], [300, 150], [450, 150], [600, 150], [750, 150], [900, 150]])
    positions.extend([[0, 300], [150, 300], [300, 300], [450, 300], [600, 300], [750, 300], [900, 300], [1050, 300]])
    positions.extend([[0, 450], [150, 450], [300, 450], [750, 450], [900, 450], [1050, 450]])
    positions.extend([[0, 600], [150, 600], [300, 600], [750, 600], [900, 600], [1050, 600]])
    positions.extend([[150, 750], [300, 750], [750, 750], [900, 750]])
    positions = np.array(positions)

    probe = Probe(
        ndim=2,
        si_units='um',
        name="32-Channel Optrode Array",
        manufacturer="Innovative Neurophysiology",
    )
    probe.set_contacts(positions=positions, shapes='circle', shape_params={'radius': 4}, contact_ids=np.arange(0, 32), shank_ids=np.zeros(32))
    probe.set_device_channel_indices(channel_indices=np.arange(0, 32))
    extractor.set_probe(probe, in_place=True)