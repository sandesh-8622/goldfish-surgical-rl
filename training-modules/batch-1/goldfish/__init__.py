"""
Goldfish: Surgical Robot Training Environment

A reinforcement learning environment for needle insertion into layered
soft tissue with biologically-informed reward functions.

Quick start:
    from goldfish.envs import NeedleInsertionEnv
    from goldfish.agents import GoldfishPPOTrainer

    env     = NeedleInsertionEnv()
    trainer = GoldfishPPOTrainer(env)
    trainer.train(total_timesteps=300_000)
    results = trainer.evaluate(n_episodes=100)
"""

__version__ = '0.2.0'

from goldfish.envs import NeedleInsertionEnv, NeedleInsertionConfig, make
from goldfish.agents import GoldfishPPOTrainer, RLAgent, BehavioralCloningAgent
from goldfish.cost_module import (
    BiologicalCostModule,
    BiologicalThresholds,
    TissueTraumaCost,
    VascularProximityCost,
    InflammationModel,
    compute_needle_insertion_score,
)
from goldfish.world_model import SimulationWorldModel, WorldModelTrainer
from goldfish.evidence import EvidenceLogger, FDASimulationLog

# Aspirational / future-work classes - architecture only, not trained
from goldfish.world_model import BiologicalWorldModel, JEPABackbone

__all__ = [
    # Environment
    'NeedleInsertionEnv',
    'NeedleInsertionConfig',
    'make',
    # Agents
    'GoldfishPPOTrainer',
    'RLAgent',
    'BehavioralCloningAgent',
    # Cost module
    'BiologicalCostModule',
    'BiologicalThresholds',
    'TissueTraumaCost',
    'VascularProximityCost',
    'InflammationModel',
    'compute_needle_insertion_score',
    # World models
    'SimulationWorldModel',
    'WorldModelTrainer',
    'BiologicalWorldModel',   # aspirational
    'JEPABackbone',           # aspirational
    # Evidence
    'EvidenceLogger',
    'FDASimulationLog',
]
