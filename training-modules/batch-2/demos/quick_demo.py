"""
Goldfish - Quick Demo  (~2 minutes, 30k timesteps)

Verifies the full pipeline runs end-to-end:
  - Kelvin-Voigt physics environment
  - SB3 PPO training
  - Evidence log export

Run from project root:
    python demos/quick_demo.py
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from demos.needle_insertion_v1 import run_training

if __name__ == '__main__':
    print("Goldfish quick demo - 30k timesteps (~2 min)")
    run_training(
        total_timesteps=30_000,
        output_dir='./quick_demo_output',
        eval_episodes=50,
    )
    print("\nOutput files in ./quick_demo_output/")
    print("  trained_policy.zip   - SB3 PPO policy (loadable)")
    print("  training_evidence.json - structured evidence log")
    print("  training_results.png - before/after comparison chart")
