"""
World Models for Goldfish

Two models provided:

1. SimulationWorldModel (USE THIS NOW)
   A compact MLP that learns to predict the next observation from
   (obs, action). Trained directly from simulation rollouts - no
   external data required. Gives the deliberative planner something
   real to work with.

2. BiologicalWorldModel / JEPABackbone (ASPIRATIONAL - future work)
   JEPA-based architecture following LeCun (2022) for predicting
   tissue response at multiple biological timescales. Architecture is
   correct; it CANNOT be used yet because it requires training data
   from real tissue experiments (cadaver studies, intraoperative
   sensors) that does not currently exist.

   We keep this code here as the design target, not as a working component.
"""

import torch
import torch.nn as nn
import numpy as np
from typing import Dict, Optional, List


# =========================================================================== #
#  1.  SimulationWorldModel  - trainable, runs today                          #
# =========================================================================== #

class SimulationWorldModel(nn.Module):
    """
    MLP world model trained on rollouts from the Goldfish simulation.

    Predicts the next 15-dim observation given (obs, action).
    Used by the deliberative planner for multi-step lookahead.

    Training:
        Collect (obs, action, next_obs) transitions from any policy.
        Minimise MSE between predicted and actual next_obs.
        1,000-10,000 transitions are typically enough to get useful predictions.
    """

    def __init__(self, obs_dim: int = 15, action_dim: int = 6, hidden_dim: int = 256):
        super().__init__()
        self.obs_dim    = obs_dim
        self.action_dim = action_dim
        self.net = nn.Sequential(
            nn.Linear(obs_dim + action_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, obs_dim),
        )
        self._init_weights()

    def _init_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.orthogonal_(m.weight, gain=0.5)
                nn.init.zeros_(m.bias)

    def forward(self, obs: torch.Tensor, action: torch.Tensor) -> torch.Tensor:
        """
        Args:
            obs:    (B, obs_dim)
            action: (B, action_dim)
        Returns:
            predicted next_obs: (B, obs_dim)
        """
        x = torch.cat([obs, action], dim=-1)
        return obs + self.net(x)   # residual: predict delta from current obs


class WorldModelTrainer:
    """
    Collects transition data from env rollouts and trains the SimulationWorldModel.

    Usage:
        trainer = WorldModelTrainer(obs_dim=15, action_dim=6)
        trainer.collect(env, n_steps=5000)
        trainer.train(epochs=50)
        # model is now usable for planning
    """

    def __init__(self, obs_dim: int = 15, action_dim: int = 6,
                 device: str = 'cuda' if torch.cuda.is_available() else 'cpu'):
        self.device = device
        self.model  = SimulationWorldModel(obs_dim, action_dim).to(device)
        self.optim  = torch.optim.Adam(self.model.parameters(), lr=3e-4)
        self.buffer: List[Dict] = []

    def collect(self, env, n_steps: int = 5000, policy=None):
        """
        Roll out the environment to collect (obs, action, next_obs) tuples.
        Uses random actions if no policy is provided.
        """
        obs, _ = env.reset()
        for _ in range(n_steps):
            if policy is not None:
                action = policy(obs)
            else:
                action = env.action_space.sample()
            next_obs, _, terminated, truncated, _ = env.step(action)
            self.buffer.append({'obs': obs, 'action': action, 'next_obs': next_obs})
            if terminated or truncated:
                obs, _ = env.reset()
            else:
                obs = next_obs
        print(f"World model buffer: {len(self.buffer)} transitions collected.")

    def train(self, epochs: int = 50, batch_size: int = 256) -> List[float]:
        if len(self.buffer) < batch_size:
            print("Not enough data to train world model.")
            return []
        losses = []
        for epoch in range(epochs):
            idx   = np.random.choice(len(self.buffer), batch_size, replace=False)
            batch = [self.buffer[i] for i in idx]
            obs      = torch.FloatTensor(np.array([b['obs']      for b in batch])).to(self.device)
            actions  = torch.FloatTensor(np.array([b['action']   for b in batch])).to(self.device)
            next_obs = torch.FloatTensor(np.array([b['next_obs'] for b in batch])).to(self.device)

            pred = self.model(obs, actions)
            loss = nn.MSELoss()(pred, next_obs)

            self.optim.zero_grad()
            loss.backward()
            self.optim.step()
            losses.append(loss.item())

        print(f"World model training - final loss: {losses[-1]:.5f}")
        return losses

    def save(self, path: str):
        torch.save(self.model.state_dict(), path)

    def load(self, path: str):
        self.model.load_state_dict(torch.load(path, map_location=self.device))


# =========================================================================== #
#  2.  JEPA Biological World Model  - aspirational, architecture only          #
# =========================================================================== #

class PatchEmbed3D(nn.Module):
    """3D patch embedding for volumetric tissue scans."""
    def __init__(self, patch_size=8, tubelet_size=2, in_chans=4, embed_dim=256):
        super().__init__()
        self.proj = nn.Conv3d(in_chans, embed_dim,
                              kernel_size=(tubelet_size, patch_size, patch_size),
                              stride=(tubelet_size, patch_size, patch_size))

    def forward(self, x):
        x = self.proj(x)
        return x.flatten(2).transpose(1, 2)


class TransformerBlock(nn.Module):
    def __init__(self, dim: int, num_heads: int, mlp_ratio: float = 4.0):
        super().__init__()
        self.norm1 = nn.LayerNorm(dim)
        self.attn  = nn.MultiheadAttention(dim, num_heads, batch_first=True)
        self.norm2 = nn.LayerNorm(dim)
        self.mlp   = nn.Sequential(
            nn.Linear(dim, int(dim * mlp_ratio)), nn.GELU(),
            nn.Linear(int(dim * mlp_ratio), dim),
        )

    def forward(self, x):
        a, _ = self.attn(self.norm1(x), self.norm1(x), self.norm1(x))
        x = x + a
        x = x + self.mlp(self.norm2(x))
        return x


class JEPABackbone(nn.Module):
    """
    JEPA encoder backbone.
    Based on: LeCun Y., "A Path Towards Autonomous Machine Intelligence." 2022.

    STATUS: Architecture correct. NOT trained. Biological predictions from
    this model are meaningless until it is trained on real tissue data.
    Training data requirements: CT/MRI scans paired with intraoperative
    force/deformation measurements and post-operative histology.
    """
    def __init__(self, img_size=64, patch_size=8, num_frames=8,
                 tubelet_size=2, in_chans=4, embed_dim=256, depth=6, num_heads=4):
        super().__init__()
        self.patch_embed = PatchEmbed3D(patch_size, tubelet_size, in_chans, embed_dim)
        n_patches = (num_frames // tubelet_size) * (img_size // patch_size) ** 2
        self.pos_embed = nn.Parameter(torch.zeros(1, n_patches, embed_dim))
        self.blocks    = nn.ModuleList([TransformerBlock(embed_dim, num_heads) for _ in range(depth)])
        self.norm      = nn.LayerNorm(embed_dim)
        nn.init.normal_(self.pos_embed, std=0.02)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.patch_embed(x) + self.pos_embed
        for blk in self.blocks:
            x = blk(x)
        return self.norm(x)


class BiologicalWorldModel(nn.Module):
    """
    JEPA-based multi-timescale biological world model.

    IMPORTANT: This model has randomly initialised weights and produces
    meaningless outputs. It is included as the architectural target for
    future work, not as a functional component.

    To make this useful you need:
        (a) A dataset of tissue deformation paired with force sensors
        (b) Post-operative outcomes to supervise the medium/long heads
        (c) A training pipeline (not included here)

    For running experiments today, use SimulationWorldModel instead.
    """

    TIMESCALES = {0: 'immediate', 1: 'short', 2: 'medium', 3: 'long'}

    def __init__(self, img_size=64, patch_size=8, num_frames=8,
                 embed_dim=256, encoder_depth=6, predictor_depth=4,
                 num_heads=4, action_dim=6):
        super().__init__()
        self.encoder = JEPABackbone(img_size, patch_size, num_frames,
                                    embed_dim=embed_dim, depth=encoder_depth,
                                    num_heads=num_heads)
        self.action_embed = nn.Linear(action_dim, embed_dim)
        # One prediction head per timescale
        self.predictors = nn.ModuleList([
            nn.Sequential(
                *[TransformerBlock(embed_dim, num_heads) for _ in range(predictor_depth)],
                nn.LayerNorm(embed_dim),
            )
            for _ in range(4)
        ])
        # Output heads (trauma, inflammation, bleeding_risk, healing_rate)
        self.output_heads = nn.ModuleList([
            nn.Linear(embed_dim, 4) for _ in range(4)
        ])

    def forward(self, tissue_state: torch.Tensor, action: torch.Tensor,
                timescale: int = 0) -> Dict[str, torch.Tensor]:
        """
        Args:
            tissue_state: (B, 4, T, H, W) - tissue volume over time
            action:       (B, action_dim)
            timescale:    0=immediate … 3=long
        Returns:
            dict with tissue_trauma, inflammation, bleeding_risk, healing_rate
        """
        enc  = self.encoder(tissue_state)             # (B, N, D)
        act  = self.action_embed(action).unsqueeze(1)  # (B, 1, D)
        ctx  = enc + act                               # broadcast add
        pred = self.predictors[timescale](ctx)
        out  = self.output_heads[timescale](pred.mean(dim=1))  # (B, 4)
        out  = torch.sigmoid(out)

        return {
            'tissue_trauma':  out[:, 0:1],
            'inflammation':   out[:, 1:2],
            'bleeding_risk':  out[:, 2:3],
            'healing_rate':   out[:, 3:4],
            'representation': pred.mean(dim=1),
        }
