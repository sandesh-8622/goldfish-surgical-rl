# goldfish - surgical robot training environment

a reinforcement learning training environment for surgical needle insertion
with biologically informed reward functions and soft tissue mechanics.

work in progress, batch 1.


## what this is

goldfish is a simulation environment where a robot agent learns to insert a
needle into layered soft tissue accurately while minimising tissue trauma and
avoiding blood vessels.

- physics model: kelvin-voigt viscoelastic layers (Okamura et al. 2004)
- RL algorithm: stable-baselines3 PPO
- observation: 15-dim compact state vector


## biological cost thresholds (all cited)

| Threshold | Value | Source |
|-----------|-------|--------|
| Max tissue strain | 0.20 (20%) | Fung 1993 |
| Max insertion force | 4.0 N | Okamura et al. 2004 |
| Min vascular distance | 3.0 mm | Abolhassani et al. 2007 |
| Max inflammatory response | 0.60 | DiMaio and Salcudean 2003 |


## honest scope

### what works today
- runnable RL training loop with real PPO
- kelvin-voigt tissue mechanics
- biologically informed reward with cited thresholds
- evidence logging with structured JSON output
- passing test suite

### what is future work
- SOFA / PhysiCell / SimVascular integration (multi-month project)
- JEPA world model training (needs real tissue data)
- FDA CMAS compliance (needs V&V studies)
