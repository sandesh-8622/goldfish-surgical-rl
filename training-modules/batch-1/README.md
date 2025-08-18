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
