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
        self.model = None

    def train(self):
        from stable_baselines3 import PPO
        from stable_baselines3.common.vec_env import DummyVecEnv

        vec_env = DummyVecEnv([lambda: self.env])
        self.model = PPO(
            "MlpPolicy",
            vec_env,
            verbose=1,
            n_steps=2048,
            batch_size=64,
            n_epochs=10,
            learning_rate=3e-4,
            gamma=0.99,
            gae_lambda=0.95,
        )
        self.model.learn(total_timesteps=self.total_timesteps)
        return self.model
