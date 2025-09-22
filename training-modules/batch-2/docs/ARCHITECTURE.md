# Goldfish Architecture Documentation

## Overview

Goldfish is a reinforcement learning training environment for surgical needle
insertion. A robot agent learns to hit a target deep in layered soft tissue
while minimising tissue trauma and staying clear of blood vessels.

**What works today:** Kelvin-Voigt tissue physics, SB3 PPO training, cited
biological cost functions, evidence logging, full test suite.

**What is future work:** SOFA/PhysiCell/SimVascular integration, JEPA world
model training on real tissue data, FDA V&V studies.

---

## Component map

```
NeedleInsertionEnv  (envs.py)
│
├── LayeredTissueSimulator
│     Kelvin-Voigt spring-damper layers (Okamura 2004)
│       soft   k=0.30 N/mm  c=0.020 N·s/mm  yield ε=0.20
│       muscle k=1.20 N/mm  c=0.080 N·s/mm  yield ε=0.15
│       fat    k=0.05 N/mm  c=0.010 N·s/mm  yield ε=0.25
│     Random vessel seeds (fixed rng=42, reproducible)
│     Observation: 15-dim compact state vector
│
└── BiologicalCostModule  (cost_module.py)
      TissueTraumaCost      strain + force excess (Fung 1993, Okamura 2004)
      VascularProximityCost exponential penalty <3 mm from vessel (Abolhassani 2007)
      InflammationModel     sigmoidal transfer: trauma → inflammation (DiMaio 2003)

GoldfishPPOTrainer  (agents.py)           ← USE THIS
  stable-baselines3 PPO
    MlpPolicy  obs_dim=15  action_dim=6
    GAE λ=0.95  γ=0.99  ent_coef=0.01  clip_range=0.2

RLAgent  (agents.py)                      ← lightweight fallback, no SB3
  Actor-critic with TD(0), manual PPO-lite

SimulationWorldModel  (world_model.py)    ← trained on sim rollouts
  Residual MLP: (obs, action) → next_obs
  WorldModelTrainer collects data + trains

BiologicalWorldModel  (world_model.py)    ← ASPIRATIONAL, random weights
  JEPA encoder + multi-timescale predictors
  Requires real tissue data to train

EvidenceLogger / FDASimulationLog  (evidence.py)
  Structured JSON output per episode
  Correct format; V&V content not yet present
```

---

## Observation space (15-dim)

| Index | Meaning | Range |
|-------|---------|-------|
| 0-2 | Needle x, y, z (normalised) | 0-1 |
| 3-5 | Target Δx, Δy, Δz (normalised) | -1 to 1 |
| 6-8 | Needle orientation unit vector | -1 to 1 |
| 9 | Tissue type (0=soft, 0.5=muscle, 1=fat) | 0-1 |
| 10 | Strain at tip | 0-1 |
| 11 | Insertion force / 5 N | 0-1 |
| 12 | Vascular proximity / 20 mm | 0-1 |
| 13 | Cumulative trauma | 0-1 |
| 14 | Time remaining (1→0) | 0-1 |

---

## Action space (6-dim, clipped to [-1, 1])

| Index | Meaning | Scale |
|-------|---------|-------|
| 0-2 | Δposition | × max_step_mm (default 2.0 mm) |
| 3-5 | Δorientation | × 0.1 rad |

---

## Biological cost thresholds (all cited)

| Parameter | Value | Source |
|-----------|-------|--------|
| Max tissue strain | 0.20 | Fung Y.C. (1993) |
| Max insertion force | 4.0 N | Okamura et al. (2004) |
| Min vascular distance | 3.0 mm | Abolhassani et al. (2007) |
| Max inflammation | 0.60 | DiMaio & Salcudean (2003) |

---

## Reward function

```
reward = progress_reward - trauma_penalty - vascular_penalty + step_penalty

progress_reward   = (prev_distance - distance) × 8.0
trauma_penalty    = max(0, strain - yield_strain) × 3.0
vascular_penalty  = max(0, 3.0mm - vascular_proximity) × 5.0
step_penalty      = -0.05

on success:
    reward += success_reward × (0.5 + 0.5 × (1 - cumulative_trauma))
    → cleaner insertions earn larger bonus
```

---

## Training pipeline

```
1. Instantiate NeedleInsertionEnv
2. Wrap in GoldfishPPOTrainer
3. trainer.train(total_timesteps=300_000)
        → SB3 PPO collects rollouts, updates policy every 2048 steps
        → TensorBoard logs in ./tb_logs/
4. trainer.evaluate(n_episodes=100)
        → returns success_rate, mean_trauma, mean_reward
5. trainer.save("my_policy")
        → saves policy.zip (loadable later)
6. env.export_evidence_log("episode.json")
        → structured JSON per episode
```

---

## Simulation world model (optional, for deliberative planning)

```python
from goldfish.world_model import WorldModelTrainer

# Collect data from a trained (or random) policy
wm_trainer = WorldModelTrainer()
wm_trainer.collect(env, n_steps=10_000)
wm_trainer.train(epochs=50)
wm_trainer.save("world_model.pt")

# Use for lookahead planning
model = wm_trainer.model
next_obs_pred = model(obs_tensor, action_tensor)
```

---

## Extensibility - adding a new procedure

1. Subclass `LayeredTissueSimulator` with procedure-specific tissue properties
2. Define a new cost function in `cost_module.py` for procedure-relevant metrics
3. Create a new `gym.Env` subclass with appropriate action/observation spaces
4. Train with `GoldfishPPOTrainer`
5. Export evidence logs for that procedure

---

## What this is NOT

- Not a high-fidelity surgical simulator (that requires SOFA/PhysiCell/SimVascular)
- Not a validated FDA submission package (requires V&V studies)
- Not a trained biological world model (requires real tissue data)
- Not a real-time robot controller (requires hardware interface layer)

These are the correct next milestones, in that order.

---

## References

1. Okamura A.M. et al. (2004). "Force modeling for needle insertion into soft tissue."
   *IEEE Trans. Biomedical Engineering* 51(10):1707-1716.

2. Fung Y.C. (1993). *Biomechanics: Mechanical Properties of Living Tissues.*
   Springer.

3. Abolhassani N. et al. (2007). "Needle insertion into soft tissue: A survey."
   *Medical Engineering & Physics* 29(4):413-431.

4. DiMaio S.P. & Salcudean S.E. (2003). "Needle insertion modelling and
   simulation." *IEEE Trans. Robotics & Automation* 19(5):864-875.

5. LeCun Y. (2022). "A Path Towards Autonomous Machine Intelligence."
   (JEPA architecture - aspirational target for world model)

6. Schmidgall S. et al. (2023). "SurgicalGym: A high-performance GPU-based
   platform for surgical robot learning." ICRA 2024.


## batch 2 outputs

batch 2 evaluation runs write to `./results/batch2/` by default. keep
batch 1 and batch 2 outputs in separate directories so you can compare
success rate, mean trauma, mean reward, and vascular safety metrics
directly between the two runs.
