# Goldfish - Surgical Robot Training Environment

A reinforcement learning training environment for surgical needle insertion
with biologically-informed reward functions and soft tissue mechanics.

## What this is

Goldfish is a **simulation environment** where a robot agent learns to insert a
needle into layered soft tissue accurately while minimising tissue trauma and
avoiding blood vessels.

**Physics model:** Kelvin-Voigt viscoelastic layers (Okamura et al. 2004).
**RL algorithm:** Stable-baselines3 PPO.
**Observation:** 15-dim compact state vector (needle position, target delta,
tissue type, strain, force, vascular proximity, trauma accumulation).

This is **batch 1 / v1** - a working, runnable foundation. It is not a
full-fidelity surgical simulator. See *Honest Scope* section below.

---

## Quick start

```bash
pip install -r requirements.txt
pip install -e .

# Quick test run (~2 min, 30k timesteps)
python demos/needle_insertion_v1.py --quick

# Full training run (300k timesteps, ~20 min on CPU)
python demos/needle_insertion_v1.py --timesteps 300000 --output ./results

# Run tests
pytest tests/test_goldfish.py -v
```

---

## Architecture

```
NeedleInsertionEnv  (envs.py)
  ├─ LayeredTissueSimulator  - Kelvin-Voigt physics
  │    soft / muscle / fat layers, randomised vessels
  └─ BiologicalCostModule    (cost_module.py)
       TissueTraumaCost       - strain + force penalties
       VascularProximityCost  - vessel proximity penalty
       InflammationModel      - trauma → inflammation estimate

GoldfishPPOTrainer  (agents.py)
  └─ stable-baselines3 PPO
       MlpPolicy, 15-dim obs, 6-dim action

SimulationWorldModel  (world_model.py)
  └─ Trained from env rollouts for deliberative planning
```

---

## Biological cost thresholds (all cited)

| Threshold | Value | Source |
|-----------|-------|--------|
| Max tissue strain | 0.20 (20 %) | Fung 1993 |
| Max insertion force | 4.0 N | Okamura et al. 2004 |
| Min vascular distance | 3.0 mm | Abolhassani et al. 2007 |
| Max inflammatory response | 0.60 | DiMaio & Salcudean 2003 |

---

## Honest scope

### What works today
- Runnable RL training loop with real PPO
- Kelvin-Voigt tissue mechanics (physically principled)
- Biologically-informed reward with cited thresholds
- Evidence logging with structured JSON output
- Passing test suite that validates behaviour, not just shapes

### What is future work
- **SOFA / PhysiCell / SimVascular integration** - these are large C++
  research frameworks. Integration is a multi-month project.
- **JEPA world model training** - the architecture is in `world_model.py`
  but requires real tissue data (cadaver studies, intraoperative sensors)
  to train. Random weights produce meaningless predictions.
- **FDA CMAS compliance** - requires Verification & Validation studies
  and clinical correlation. The JSON log format is correct; the V&V
  content does not yet exist.

---

## Project structure

```
goldfish/
├── goldfish/
│   ├── envs.py          Kelvin-Voigt environment + Gym registration
│   ├── cost_module.py   Cited biological cost functions
│   ├── agents.py        GoldfishPPOTrainer (SB3) + lightweight RLAgent
│   ├── world_model.py   SimulationWorldModel + JEPA (aspirational)
│   └── evidence.py      FDA-format JSON logging
├── demos/
│   └── needle_insertion_v1.py   Main training demo
├── tests/
│   └── test_goldfish.py         Behavioural test suite
└── docs/
    └── ARCHITECTURE.md          Technical documentation
```

---

## Research foundation

- Okamura A.M. et al. (2004) - needle insertion force modelling
- Fung Y.C. (1993) - soft tissue biomechanics
- Abolhassani N. et al. (2007) - needle insertion survey
- LeCun Y. (2022) - JEPA world model architecture (aspirational)
- Schmidgall S. (2023) - SurgicalGym GPU-accelerated simulation


---

status: batch 2 v1, runnable research module.

## acknowledgments

thanks to the SurgicalGym team for the simulation framework reference,
and to the Okamura and Fung papers for the foundational biomechanics work.
