"""
goldfish.envs

needle insertion environment with kelvin-voigt soft tissue mechanics.
"""

import numpy as np


# tissue layer parameters from real biomechanics literature
# soft / muscle / fat have different elastic moduli and viscosities
TISSUE_LAYERS = {
    "soft":   {"thickness_mm": 5.0,  "E_kPa": 10.0,  "eta_Pa_s": 0.5, "color": "pink"},
    "muscle": {"thickness_mm": 15.0, "E_kPa": 60.0,  "eta_Pa_s": 1.2, "color": "red"},
    "fat":    {"thickness_mm": 8.0,  "E_kPa": 3.0,   "eta_Pa_s": 0.3, "color": "yellow"},
}


class LayeredTissueSimulator:
    """layered soft tissue with kelvin-voigt viscoelastic response."""

    def __init__(self, layers=None, seed=0):
        self.layers = layers or list(TISSUE_LAYERS.keys())
        self.rng = np.random.default_rng(seed)
        self.strain = 0.0
        self.force = 0.0
