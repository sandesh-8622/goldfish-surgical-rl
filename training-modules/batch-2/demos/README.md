# Goldfish v1 Demo Documentation

## Overview

This is the v1 demonstration of Goldfish - a complete biological simulation environment for surgical robot training.

**Target Task:** Needle Insertion into Soft Tissue  
**Episodes:** 10,000  
**Goal:** Demonstrate robot agent improving accuracy while reducing biological harm

## Demo Structure

```
demos/
├── needle_insertion_v1.py          # Main training script
├── quick_demo.py                   # 100-episode test
├── visualize_results.py            # Plot generation
└── evidence_analysis.py            # FDA log analysis
```

## Running the Demo

### Full Demo (10,000 episodes)

```bash
python demos/needle_insertion_v1.py --episodes 10000 --output ./v1_results
```

### Quick Test (100 episodes)

```bash
python demos/needle_insertion_v1.py --quick
```

### Custom Configuration

```python
from demos.needle_insertion_v1 import train_needle_insertion_agent

results = train_needle_insertion_agent(
    num_episodes=5000,
    eval_interval=100,
    save_dir='./my_results',
    device='cuda',
)
```

## What the Demo Shows

### 1. Agent Training Progress

The robot agent learns to:
- Insert needle to target depth (50mm ± 3mm tolerance)
- Minimize lateral error (within 5mm)
- Avoid excessive tissue trauma
- Maintain safe distance from vascular structures

### 2. Biological Outcome Tracking

For every episode, we track:
- **Tissue trauma** (0-1, lower is better)
- **Inflammation score** (predicted immune response)
- **Vascular proximity** (distance to blood vessels)
- **Recovery trajectory** (predicted healing outcome)
- **Comprehensive insertion score** (weighted combination)

### 3. FDA-Compatible Evidence Logs

Each episode generates structured logs including:
- Complete step-by-step biological metrics
- Statistical summaries
- Uncertainty characterization
- CMAS framework alignment

## Expected Results

After 10,000 episodes:
- **Success rate:** 80-90% (needle reaches target within tolerance)
- **Tissue trauma reduction:** 40-50% compared to early episodes
- **Recovery score improvement:** 30-40% improvement
- **Evidence logs:** Ready for regulatory submission format

## Key Metrics

### Training Curves Generated

1. **Reward vs Episode** - Shows learning progress
2. **Success Rate vs Episode** - Task completion rate
3. **Tissue Trauma vs Episode** - Biological harm reduction
4. **Insertion Score vs Episode** - Comprehensive quality metric

### Biological Thresholds

The agent learns to respect:
- Maximum tissue strain: 30%
- Maximum cutting force: 5N
- Minimum vascular distance: 2mm
- Maximum inflammation response: 70%

## Demo Output

```
demo_output/
├── training_curves.png         # Visualization of learning
├── trained_policy.pt           # Trained RL agent
├── training_evidence.json      # FDA-compatible logs
└── demo_report.json            # Summary statistics
```

## Interpretation

### What Success Looks Like

**Good Demo:**
- Success rate increases monotonically
- Tissue trauma decreases over time
- Agent occasionally fails early, rarely fails late
- Evidence logs contain 10,000 complete episodes

**Concerning Patterns:**
- Success rate flat or decreasing (learning not occurring)
- Tissue trauma increasing (agent exploiting simulator)
- High variance without convergence (instability)

### Biological Plausibility

The demo uses simplified tissue models. In production:
- SOFA for soft tissue mechanics
- PhysiCell for cellular response
- SimVascular for blood flow
- Real patient data for model calibration

## Next Steps After Demo

1. **Validation:** Compare simulation outcomes to ex vivo tissue experiments
2. **Expansion:** Add more procedure types (suturing, cutting, cauterization)
3. **Integration:** Connect with physical surgical robots (dVRK, da Vinci)
4. **Regulatory:** Submit evidence package for FDA pre-submission meeting

## Technical Details

### World Model

- Architecture: JEPA (Joint Embedding Predictive Architecture)
- Input: 4-channel tissue state (type, strain, vascularity, inflammation)
- Output: Biological predictions at 4 timescales
- Training: Self-supervised on simulation rollouts

### Agent

- Algorithm: PPO-style policy gradient
- Policy network: 256-dimensional hidden layers
- Value network: Critic for advantage estimation
- Training: Online updates every 10 steps

### Cost Module

- Intrinsic costs: Fixed clinical thresholds
- Learned critic: Predicts recovery outcomes
- Combined: Weighted sum guides policy optimization

## Citation

If you use this demo in research:

```bibtex
@software{goldfish2026,
  title={Goldfish: Biological Simulation Environment for Surgical Robotics},
  author={[Goldfish Team]},
  year={2026},
  url={https://goldfish.simulation}
}
```

## Contact

For questions about the demo: [team@goldfish.simulation]
