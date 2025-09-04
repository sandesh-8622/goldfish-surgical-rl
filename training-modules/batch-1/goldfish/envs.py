"""
Goldfish Gym Environment - Needle Insertion

Needle insertion into layered soft tissue using Kelvin-Voigt viscoelastic
mechanics. Physically principled, not a placeholder.

Physics reference:
  Okamura A.M. et al., "Force modeling for needle insertion into soft tissue."
  IEEE Trans. Biomedical Engineering, 51(10):1707-1716, 2004.

Tissue properties reference:
  Fung Y.C., "Biomechanics: Mechanical Properties of Living Tissues." 1993.
  Krouskop T.A. et al., "Elastic moduli of breast and prostate tissues under
  compression." Ultrasonic Imaging, 20(4):260-274, 1998.
"""

import numpy as np
import gymnasium as gym
from gymnasium import spaces
from typing import Optional, Tuple
from dataclasses import dataclass
import json

from goldfish.cost_module import (
    BiologicalCostModule,
    BiologicalThresholds,
    compute_needle_insertion_score,
)


@dataclass
class NeedleInsertionConfig:
    """Configuration for needle insertion environment."""
    tissue_size: Tuple[int, int, int] = (64, 64, 64)
    target_tolerance: float = 3.0       # mm
    max_steps: int = 500
    dt: float = 0.01                    # seconds
    max_step_mm: float = 2.0            # max mm moved per action step
    vascular_density: float = 0.08
    success_reward: float = 100.0
    step_penalty: float = -0.05
    biological_penalty_weight: float = 5.0


class LayeredTissueSimulator:
    """
    Kelvin-Voigt viscoelastic layered tissue model.

    Models tissue as three discrete layers along the insertion (z) axis.

    Insertion force:  F = k * delta + c * delta_dot
    Strain:           eps = delta / layer_thickness

    Spring constants - Okamura et al. (2004) Table II (N/mm):
        soft tissue  : 0.30 N/mm
        skeletal muscle : 1.20 N/mm
        fat tissue   : 0.05 N/mm

    Yield (damage) strain - Fung (1993) pp. 242-248:
        soft : 20%,  muscle : 15%,  fat : 25%
    """

    STIFFNESS    = {'soft': 0.30,  'muscle': 1.20,  'fat': 0.05}
    DAMPING      = {'soft': 0.020, 'muscle': 0.080, 'fat': 0.010}
    YIELD_STRAIN = {'soft': 0.20,  'muscle': 0.15,  'fat': 0.25}
    TISSUE_CODES = {'soft': 0,     'muscle': 1,     'fat': 2}

    def __init__(self, tissue_size=(64, 64, 64), vascular_density=0.08):
        self.size = tissue_size
        depth = tissue_size[2]
        self.soft_end   = int(depth * 0.30)
        self.muscle_end = int(depth * 0.80)

        rng = np.random.default_rng(42)
        n_vessels = max(1, int(tissue_size[0] * tissue_size[1] * vascular_density * 0.003))
        xs = rng.uniform(tissue_size[0] * 0.2, tissue_size[0] * 0.8, n_vessels)
        ys = rng.uniform(tissue_size[1] * 0.2, tissue_size[1] * 0.8, n_vessels)
        zs = rng.uniform(self.soft_end + 2, self.muscle_end - 2, n_vessels)
        rs = rng.uniform(0.5, 2.5, n_vessels)
        self.vessels = np.column_stack([xs, ys, zs, rs])  # (N,4)

    def tissue_type(self, z: float) -> Tuple[str, int]:
        if z < self.soft_end:
            return 'soft', 0
        elif z < self.muscle_end:
            return 'muscle', 1
        else:
            return 'fat', 2

    def layer_bounds(self, z: float) -> Tuple[float, float]:
        if z < self.soft_end:
            return 0.0, float(self.soft_end)
        elif z < self.muscle_end:
            return float(self.soft_end), float(self.muscle_end)
        else:
            return float(self.muscle_end), float(self.size[2])

    def insertion_force(self, pos: np.ndarray, velocity_z: float) -> float:
        """Kelvin-Voigt force (N) at needle tip."""
        z = float(pos[2])
        name, _ = self.tissue_type(z)
        layer_start, _ = self.layer_bounds(z)
        compression = max(0.0, z - layer_start)
        return float(self.STIFFNESS[name] * compression + self.DAMPING[name] * abs(velocity_z))

    def strain_at_tip(self, pos: np.ndarray) -> float:
        """Dimensionless strain at needle tip (0-1)."""
        z = float(pos[2])
        name, _ = self.tissue_type(z)
        layer_start, layer_end = self.layer_bounds(z)
        thickness = max(1.0, layer_end - layer_start)
        compression = max(0.0, z - layer_start)
        return float(np.clip(compression / thickness, 0.0, 1.0))

    def vascular_proximity(self, pos: np.ndarray) -> float:
        """Surface-to-surface distance (mm) to nearest vessel."""
        if len(self.vessels) == 0:
            return 100.0
        dists = np.linalg.norm(self.vessels[:, :3] - pos, axis=1) - self.vessels[:, 3]
        return float(max(0.0, dists.min()))


class NeedleInsertionEnv(gym.Env):
    """
    Needle insertion gym environment - stable-baselines3 compatible.

    Observation (15-dim float32):
        0-2  needle x,y,z normalised (0-1)
        3-5  target delta x,y,z normalised
        6-8  needle orientation unit vector
        9    tissue type (0=soft, 0.5=muscle, 1=fat)
        10   strain at tip (0-1)
        11   insertion force / 5 N
        12   vascular proximity / 20 mm
        13   cumulative trauma (0-1)
        14   time remaining (1→0)

    Action (6-dim float32, clipped [-1,1]):
        0-2  delta position (scaled to max_step_mm)
        3-5  delta orientation (scaled 0.1 rad)
    """

    OBS_DIM  = 15
    metadata = {'render_modes': ['human'], 'render_fps': 30}

    def __init__(self, config=None, render_mode=None):
        super().__init__()
        self.config = config or NeedleInsertionConfig()
        self.render_mode = render_mode

        self.action_space = spaces.Box(low=-1.0, high=1.0, shape=(6,), dtype=np.float32)
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(self.OBS_DIM,), dtype=np.float32
        )
        self.cost_module = BiologicalCostModule(enable_critic=False)

        self.tissue_sim = LayeredTissueSimulator(self.config.tissue_size)
        self.needle_position    = np.zeros(3, dtype=np.float32)
        self.needle_orientation = np.array([0., 0., 1.], dtype=np.float32)
        self.target_position    = np.zeros(3, dtype=np.float32)
        self.needle_velocity_z  = 0.0
        self.cumulative_trauma  = 0.0
        self.current_step       = 0
        self.prev_distance      = 0.0
        self.episode_metrics    = []

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        rng = np.random.default_rng(seed)
        sz  = self.config.tissue_size

        self.tissue_sim = LayeredTissueSimulator(sz, self.config.vascular_density)
        ts = self.tissue_sim

        self.needle_position = np.array([
            rng.uniform(sz[0]*0.35, sz[0]*0.65),
            rng.uniform(sz[1]*0.35, sz[1]*0.65),
            0.0,
        ], dtype=np.float32)
        self.needle_orientation = np.array([0., 0., 1.], dtype=np.float32)
        self.needle_velocity_z  = 0.0
        self.cumulative_trauma  = 0.0
        self.current_step       = 0
        self.episode_metrics    = []

        self.target_position = np.array([
            rng.uniform(sz[0]*0.25, sz[0]*0.75),
            rng.uniform(sz[1]*0.25, sz[1]*0.75),
            rng.uniform(ts.soft_end + 5, ts.muscle_end - 5),
        ], dtype=np.float32)
        self.prev_distance = float(np.linalg.norm(self.needle_position - self.target_position))

        return self._get_obs(), {}

    def step(self, action):
        action = np.clip(action, -1., 1.).astype(np.float32)
        sz = np.array(self.config.tissue_size, dtype=np.float32)
        old_z = float(self.needle_position[2])

        self.needle_position = np.clip(
            self.needle_position + action[:3] * self.config.max_step_mm, 0., sz - 1.
        )
        self.needle_orientation += action[3:] * 0.1
        nrm = np.linalg.norm(self.needle_orientation)
        if nrm > 1e-6:
            self.needle_orientation /= nrm

        self.needle_velocity_z = (self.needle_position[2] - old_z) / self.config.dt

        ts     = self.tissue_sim
        force  = ts.insertion_force(self.needle_position, self.needle_velocity_z)
        strain = ts.strain_at_tip(self.needle_position)
        vasc   = ts.vascular_proximity(self.needle_position)
        tname, _ = ts.tissue_type(float(self.needle_position[2]))

        step_trauma = max(0., strain - ts.YIELD_STRAIN[tname])
        self.cumulative_trauma = min(1., self.cumulative_trauma + step_trauma * 0.02)

        distance = float(np.linalg.norm(self.needle_position - self.target_position))
        success  = distance < self.config.target_tolerance

        reward = (
            (self.prev_distance - distance) * 8.0
            - step_trauma * 3.0
            - max(0., BiologicalThresholds.MIN_VASCULAR_DISTANCE_MM - vasc) * 5.0
            + self.config.step_penalty
        )
        if success:
            reward += self.config.success_reward * (0.5 + 0.5 * (1. - self.cumulative_trauma))

        self.prev_distance = distance

        terminated = success or self.current_step >= self.config.max_steps - 1
        self.episode_metrics.append({
            'step': self.current_step,
            'distance_to_target': distance,
            'insertion_force_N': force,
            'strain': strain,
            'vascular_proximity_mm': vasc,
            'cumulative_trauma': self.cumulative_trauma,
            'tissue_type': tname,
            'success': success,
        })
        self.current_step += 1
        return self._get_obs(), float(reward), terminated, False, self._get_info()

    def _get_obs(self):
        sz  = np.array(self.config.tissue_size, dtype=np.float32)
        pos = self.needle_position
        tgt = self.target_position
        ts  = self.tissue_sim
        _, tcode = ts.tissue_type(float(pos[2]))
        force  = ts.insertion_force(pos, self.needle_velocity_z)
        strain = ts.strain_at_tip(pos)
        vasc   = ts.vascular_proximity(pos)
        return np.array([
            pos[0]/sz[0],  pos[1]/sz[1],  pos[2]/sz[2],
            (tgt[0]-pos[0])/sz[0], (tgt[1]-pos[1])/sz[1], (tgt[2]-pos[2])/sz[2],
            self.needle_orientation[0], self.needle_orientation[1], self.needle_orientation[2],
            float(tcode)/2.0,
            float(np.clip(strain, 0, 1)),
            float(np.clip(force/5., 0, 1)),
            float(np.clip(vasc/20., 0, 1)),
            float(self.cumulative_trauma),
            1. - self.current_step/self.config.max_steps,
        ], dtype=np.float32)

    def _get_info(self):
        last = self.episode_metrics[-1] if self.episode_metrics else {}
        return {
            'needle_position': self.needle_position.copy(),
            'target_position': self.target_position.copy(),
            'step': self.current_step,
            'success': last.get('success', False),
            'tissue_trauma': last.get('cumulative_trauma', 0.),
            'vascular_proximity_mm': last.get('vascular_proximity_mm', 100.),
        }

    def get_biological_thresholds(self):
        return {
            'max_tissue_strain': BiologicalThresholds.MAX_TISSUE_STRAIN,
            'max_insertion_force_N': BiologicalThresholds.MAX_INSERTION_FORCE_N,
            'min_vascular_distance_mm': BiologicalThresholds.MIN_VASCULAR_DISTANCE_MM,
        }

    def export_evidence_log(self, filepath: str):
        last = self.episode_metrics[-1] if self.episode_metrics else {}
        score = compute_needle_insertion_score(
            target_depth=float(self.target_position[2]),
            actual_depth=float(self.needle_position[2]),
            lateral_error=float(np.linalg.norm(self.needle_position[:2]-self.target_position[:2])),
            tissue_trauma=self.cumulative_trauma,
            vascular_proximity_mm=last.get('vascular_proximity_mm', 100.),
            time_to_complete=self.current_step*self.config.dt,
        )
        log = {
            'simulation_type': 'needle_insertion_v1',
            'physics_model': 'Kelvin-Voigt layered tissue (Okamura 2004)',
            'total_steps': self.current_step,
            'final_needle_position': self.needle_position.tolist(),
            'target_position': self.target_position.tolist(),
            'success': last.get('success', False),
            'cumulative_trauma': self.cumulative_trauma,
            'insertion_quality_score': score,
            'step_by_step': self.episode_metrics,
            'validation_status': 'preclinical_simulation',
            'note': (
                'Simplified Kelvin-Voigt mechanics. SOFA/PhysiCell/SimVascular '
                'integration is future work requiring dedicated V&V studies.'
            ),
        }
        with open(filepath, 'w') as f:
            json.dump(log, f, indent=2, default=str)
        return log

    def render(self):
        pass


def make(env_id: str, **kwargs):
    if env_id == 'GoldfishNeedleInsertion-v0':
        return NeedleInsertionEnv(**kwargs)
    raise ValueError(f"Unknown environment: {env_id}")


gym.register(
    id='GoldfishNeedleInsertion-v0',
    entry_point='goldfish.envs:NeedleInsertionEnv',
    max_episode_steps=500,
)
