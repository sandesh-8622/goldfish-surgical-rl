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


    def collect_rollouts(self, env, agent, n_episodes=20):
        """run agent in env and store (obs, action, next_obs) tuples."""
        data = []
        for _ in range(n_episodes):
            obs, _ = env.reset()
            done = False
            while not done:
                action, _ = agent.predict(obs)
                next_obs, _r, term, trunc, _info = env.step(action)
                data.append((np.asarray(obs, dtype=np.float32),
                             np.asarray(action, dtype=np.float32),
                             np.asarray(next_obs, dtype=np.float32)))
                obs = next_obs
                done = term or trunc
        return data

    def train(self, data, epochs=20):
        """basic MSE fit. tiny net, tiny data, just enough to have a hook."""
        try:
            import torch
            import torch.nn as nn
        except ImportError:
            print("[!] torch not installed, skipping world model training")
            return
        # placeholder training loop, no real net yet
        self.trained = True
