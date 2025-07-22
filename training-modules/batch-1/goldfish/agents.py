"""
goldfish.agents

ppo trainer (stable-baselines3) and a lightweight fallback agent.
"""

import os
import numpy as np


class GoldfishPPOTrainer:
    """wraps stable-baselines3 PPO with goldfish-specific defaults."""

    def __init__(self, env, total_timesteps=300_000, output_dir="./results"):
        self.env = env
        self.total_timesteps = total_timesteps
        self.output_dir = output_dir
