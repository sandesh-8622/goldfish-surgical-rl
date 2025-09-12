"""
Robot Agent Interfaces for Goldfish

Primary trainer: GoldfishPPOTrainer (uses stable-baselines3 PPO - proven,
publication-grade RL with correct advantage estimation, entropy bonus,
gradient clipping, and proper PPO clipping).

Custom agents (RLAgent, BehavioralCloningAgent) are kept as lightweight
alternatives if you cannot install SB3.
"""

import os
import numpy as np
import torch
import torch.nn as nn
from typing import Dict, List, Optional


# --------------------------------------------------------------------------- #
#  Primary: SB3-based PPO trainer                                              #
# --------------------------------------------------------------------------- #

class GoldfishPPOTrainer:
    """
    Train a needle insertion policy using stable-baselines3 PPO.

    Why SB3 over a custom agent?
    - Correct GAE advantage estimation
    - Proper entropy bonus (prevents premature convergence)
    - Gradient clipping + learning rate schedule
    - Tested on hundreds of gym environments

    Usage:
        trainer = GoldfishPPOTrainer(env)
        trainer.train(total_timesteps=300_000)
        trainer.save("my_policy")
        results = trainer.evaluate(n_episodes=100)
    """

    def __init__(self, env, tensorboard_log: str = "./tb_logs/", device: str = "auto"):
        try:
            from stable_baselines3 import PPO
            from stable_baselines3.common.monitor import Monitor
        except ImportError:
            raise ImportError(
                "stable-baselines3 is required. Run: pip install stable-baselines3[extra]"
            )
        self.env = Monitor(env)
        self.model = PPO(
            "MlpPolicy",
            self.env,
            verbose=1,
            learning_rate=3e-4,
            n_steps=2048,
            batch_size=64,
            n_epochs=10,
            gamma=0.99,
            gae_lambda=0.95,
            clip_range=0.2,
            ent_coef=0.01,          # entropy bonus - prevents stagnation
            tensorboard_log=tensorboard_log,
            device=device,
        )

    def train(self, total_timesteps: int = 300_000, callback=None):
        """
        Train the policy.

        300 000 timesteps ≈ 600 episodes of 500 steps.
        Expect visible improvement within the first 50 k steps.
        """
        self.model.learn(total_timesteps=total_timesteps, callback=callback)
        return self

    def save(self, path: str):
        self.model.save(path)
        print(f"Policy saved to {path}.zip")

    @classmethod
    def load(cls, path: str, env):
        from stable_baselines3 import PPO
        from stable_baselines3.common.monitor import Monitor
        instance = cls.__new__(cls)
        instance.env = Monitor(env)
        instance.model = PPO.load(path, env=instance.env)
        return instance

    def predict(self, obs: np.ndarray, deterministic: bool = True) -> np.ndarray:
        action, _ = self.model.predict(obs, deterministic=deterministic)
        return action

    def evaluate(self, n_episodes: int = 100) -> Dict:
        """Run n_episodes and return performance statistics."""
        rewards, successes, traumas = [], [], []

        for _ in range(n_episodes):
            obs, _ = self.env.reset()
            ep_reward, done = 0.0, False
            while not done:
                action = self.predict(obs)
                obs, r, terminated, truncated, info = self.env.step(action)
                ep_reward += r
                done = terminated or truncated
            rewards.append(ep_reward)
            successes.append(float(info.get('success', False)))
            traumas.append(float(info.get('tissue_trauma', 0.)))

        return {
            'mean_reward':   float(np.mean(rewards)),
            'std_reward':    float(np.std(rewards)),
            'success_rate':  float(np.mean(successes)),
            'mean_trauma':   float(np.mean(traumas)),
            'n_episodes':    n_episodes,
        }


# --------------------------------------------------------------------------- #
#  Lightweight custom RL agent (fallback, no SB3 required)                    #
# --------------------------------------------------------------------------- #

class ReactivePolicy(nn.Module):
    """Simple MLP policy: obs → action in tanh(-1, 1)."""

    def __init__(self, obs_dim: int, action_dim: int, hidden_dim: int = 256):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(obs_dim, hidden_dim), nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim), nn.ReLU(),
            nn.Linear(hidden_dim, action_dim), nn.Tanh(),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


class RLAgent:
    """
    Lightweight actor-critic agent.

    Uses TD(0) value updates + behavioural cloning-style policy gradient.
    Correct for simple experiments; use GoldfishPPOTrainer for serious runs.
    """

    def __init__(self, obs_dim: int, action_dim: int,
                 lr: float = 3e-4,
                 device: str = 'cuda' if torch.cuda.is_available() else 'cpu'):
        self.device = device
        self.policy = ReactivePolicy(obs_dim, action_dim).to(device)
        self.value  = nn.Sequential(
            nn.Linear(obs_dim, 256), nn.ReLU(),
            nn.Linear(256, 256),    nn.ReLU(),
            nn.Linear(256, 1),
        ).to(device)
        self.p_opt  = torch.optim.Adam(self.policy.parameters(), lr=lr)
        self.v_opt  = torch.optim.Adam(self.value.parameters(),  lr=lr)
        self.buffer: List[Dict] = []

    def reset(self):
        self.buffer = []

    def predict(self, obs: np.ndarray) -> np.ndarray:
        with torch.no_grad():
            t = torch.FloatTensor(obs).unsqueeze(0).to(self.device)
            a = self.policy(t).cpu().numpy()[0]
        return a + np.random.randn(a.shape[0]) * 0.05

    def update(self, experience: Dict):
        self.buffer.append(experience)

    def train_step(self, batch_size: int = 64):
        if len(self.buffer) < batch_size:
            return {}
        idx   = np.random.choice(len(self.buffer), batch_size, replace=False)
        batch = [self.buffer[i] for i in idx]

        obs      = torch.FloatTensor(np.array([e['observation']      for e in batch])).to(self.device)
        actions  = torch.FloatTensor(np.array([e['action']           for e in batch])).to(self.device)
        rewards  = torch.FloatTensor(np.array([e['reward']           for e in batch])).to(self.device)
        next_obs = torch.FloatTensor(np.array([e['next_observation'] for e in batch])).to(self.device)
        dones    = torch.FloatTensor(np.array([e['done']             for e in batch])).to(self.device)

        with torch.no_grad():
            next_v = self.value(next_obs).squeeze()
        td_target  = rewards + 0.99 * next_v * (1. - dones)
        v_loss     = nn.MSELoss()(self.value(obs).squeeze(), td_target)
        p_loss     = nn.MSELoss()(self.policy(obs), actions)
        loss       = p_loss + 0.5 * v_loss

        self.p_opt.zero_grad(); self.v_opt.zero_grad()
        loss.backward()
        self.p_opt.step(); self.v_opt.step()

        return {'policy_loss': p_loss.item(), 'value_loss': v_loss.item()}

    def save(self, path: str):
        torch.save({'policy': self.policy.state_dict(),
                    'value':  self.value.state_dict()}, path)

    def load(self, path: str):
        ckpt = torch.load(path, map_location=self.device)
        self.policy.load_state_dict(ckpt['policy'])
        self.value.load_state_dict(ckpt['value'])


# --------------------------------------------------------------------------- #
#  Behavioural cloning (pre-train from expert demos before RL fine-tuning)    #
# --------------------------------------------------------------------------- #

class BehavioralCloningAgent:
    """
    Initialise a policy from expert demonstrations (imitation learning).
    Useful to warm-start RL training, cutting sample complexity significantly.
    """

    def __init__(self, obs_dim: int, action_dim: int):
        self.policy = ReactivePolicy(obs_dim, action_dim)
        self.opt    = torch.optim.Adam(self.policy.parameters(), lr=3e-4)
        self.demos: List[Dict] = []

    def add_demo(self, obs: np.ndarray, expert_action: np.ndarray):
        self.demos.append({'obs': obs, 'action': expert_action})

    def train(self, epochs: int = 100, batch_size: int = 64) -> Dict:
        if len(self.demos) < batch_size:
            return {}
        losses = []
        for _ in range(epochs):
            idx   = np.random.choice(len(self.demos), batch_size, replace=False)
            batch = [self.demos[i] for i in idx]
            obs = torch.FloatTensor(np.array([d['obs']    for d in batch]))
            act = torch.FloatTensor(np.array([d['action'] for d in batch]))
            loss = nn.MSELoss()(self.policy(obs), act)
            self.opt.zero_grad(); loss.backward(); self.opt.step()
            losses.append(loss.item())
        return {'mean_bc_loss': float(np.mean(losses))}

    def to_rl_agent(self, obs_dim: int, action_dim: int) -> RLAgent:
        """Transfer policy weights to an RLAgent for RL fine-tuning."""
        agent = RLAgent(obs_dim, action_dim)
        agent.policy.load_state_dict(self.policy.state_dict())
        return agent
