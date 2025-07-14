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



class NeedleInsertionEnv:
    """gym-compatible env for needle insertion training.

    observation (15-dim):
      0-2   needle tip position xyz
      3-5   target position delta xyz
      6     tissue type id (0/1/2)
      7     current strain
      8     current insertion force
      9-11  vascular proximity vector
      12    accumulated trauma score
      13    inflammation estimate
      14    timestep ratio
    """

    def __init__(self):
        self.tissue = LayeredTissueSimulator()
        self.step_count = 0

    def reset(self):
        self.tissue = LayeredTissueSimulator()
        self.step_count = 0
        return self._get_obs()

    def step(self, action):
        self.step_count += 1
        obs = self._get_obs()
        reward = 0.0
        done = False
        info = {}
        return obs, reward, done, info

    def _get_obs(self):
        return np.zeros(15, dtype=np.float32)
