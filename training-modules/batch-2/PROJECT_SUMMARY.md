# Goldfish Batch 2 Project Summary

## Project Overview

Goldfish Batch 2 is the Kelvin-Voigt continuation package for the surgical
needle-insertion training environment. It keeps the training target narrow and
measurable: a robot agent learns to insert a needle into layered soft tissue
while minimizing tissue trauma and avoiding vascular structures.

This package is technical documentation and runnable code only. Non-technical
application and fundraising materials have been removed from the deliverable.

---

## What Is Included

### Core Platform (`goldfish/`)

| Component | File | Description |
|-----------|------|-------------|
| Needle insertion environment | `envs.py` | Gym-compatible environment with Kelvin-Voigt tissue mechanics |
| Biological costs | `cost_module.py` | Trauma, insertion force, vascular proximity, and inflammation scoring |
| Robot agents | `agents.py` | Stable-Baselines3 PPO trainer and lightweight fallback agent |
| World model | `world_model.py` | Rollout-trained simulation world model plus aspirational biological model scaffold |
| Evidence logging | `evidence.py` | Structured JSON logs for simulation runs and evaluation outputs |

### Demos (`demos/`)

| File | Purpose |
|------|---------|
| `needle_insertion_v1.py` | Main training demo for quick or full PPO runs |
| `quick_demo.py` | Short verification run for checking the environment |
| `README.md` | Demo instructions and interpretation notes |

### Documentation (`docs/`)

| File | Content |
|------|---------|
| `ARCHITECTURE.md` | Observation space, action space, reward function, pipeline, and limits |

### Tests (`tests/`)

| File | Coverage |
|------|----------|
| `test_goldfish.py` | Core environment and component behavior |

---

## How To Run

```bash
pip install -r requirements.txt
pip install -e .

# Quick verification run
python demos/needle_insertion_v1.py --quick

# Full training run
python demos/needle_insertion_v1.py --timesteps 300000 --output ./results

# Run tests
pytest tests/test_goldfish.py -v
```

---

## Expected Outputs

Training and evaluation runs should produce a combination of policy artifacts,
summary statistics, and structured evidence logs. Keep Batch 2 outputs in a
separate directory from Batch 1 so success rate, mean trauma, mean reward, and
vascular safety metrics can be compared directly.

Recommended output layout:

```text
results/
  batch2_policy.zip
  batch2_evaluation.json
  batch2_evidence_log.json
  tensorboard/
```

---

## Honest Scope

What works now:

- Runnable PPO training loop
- Kelvin-Voigt tissue layer mechanics
- Biologically informed reward and cost functions
- Structured simulation evidence logs
- Tests for core behavior

What remains future work:

- High-fidelity SOFA, PhysiCell, and SimVascular integration
- JEPA biological world model training on real tissue data
- FDA verification and validation studies
- Hardware robot control interfaces

---

## Research Foundation

- Okamura et al. (2004): needle insertion force modeling
- Fung (1993): soft tissue biomechanics
- Abolhassani et al. (2007): needle insertion survey
- DiMaio and Salcudean (2003): needle insertion modeling and simulation
- LeCun (2022): JEPA world model architecture target
- Schmidgall et al. (2023): SurgicalGym simulation platform

---

## Status

Project status: runnable research module.

Use Batch 2 as a separate trained-module continuation from Batch 1. Do not mix
checkpoints, logs, or evaluation outputs between batches.

## reproducibility

seed all random sources via the rng arg on env reset. evaluation runs should be done with deterministic=True on the policy to remove sampling noise.

## changelog

- 2025-09: batch 2 v1, continuation of batch 1, same scope.

## handoff

this batch is ready to compare against batch 1 outputs side by side.
keep checkpoint files and evidence logs separate, do not mix them.
