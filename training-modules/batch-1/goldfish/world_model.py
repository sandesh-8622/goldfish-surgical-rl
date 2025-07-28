"""
goldfish.world_model

simulation world model trained from env rollouts. lets the agent plan
without paying the cost of stepping the real env.

there's also a JEPA-shaped scaffold here, but it is aspirational. the
real architecture is from LeCun 2022, and training it would need real
tissue data we don't have.
"""

import numpy as np


class SimulationWorldModel:
    """tiny neural net that predicts next observation given current obs + action."""

    def __init__(self, obs_dim=15, action_dim=6, hidden=128):
        self.obs_dim = obs_dim
        self.action_dim = action_dim
        self.hidden = hidden
        self.trained = False
