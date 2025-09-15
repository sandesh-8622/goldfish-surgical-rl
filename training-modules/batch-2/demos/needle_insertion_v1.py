"""
Needle Insertion v1 - Full Training Demo

Uses stable-baselines3 PPO for real, publication-grade RL training.
Physics: Kelvin-Voigt layered tissue (Okamura 2004).
Reward: Distance-to-target + biological cost penalties.

Run:
    python demos/needle_insertion_v1.py --timesteps 300000 --output ./demo_output
    python demos/needle_insertion_v1.py --quick          # 30k steps, ~2 min
"""

import argparse
import os
import json
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict

from goldfish.envs import NeedleInsertionEnv, NeedleInsertionConfig
from goldfish.agents import GoldfishPPOTrainer


def run_training(
    total_timesteps: int = 300_000,
    output_dir: str = './demo_output',
    eval_episodes: int = 100,
) -> Dict:

    os.makedirs(output_dir, exist_ok=True)

    print("=" * 60)
    print("Goldfish - Needle Insertion v1")
    print(f"  Timesteps : {total_timesteps:,}")
    print(f"  Output    : {output_dir}")
    print(f"  Physics   : Kelvin-Voigt layered tissue (Okamura 2004)")
    print("=" * 60)

    config = NeedleInsertionConfig(
        tissue_size=(64, 64, 64),
        target_tolerance=3.0,
        max_steps=500,
        vascular_density=0.08,
    )
    env = NeedleInsertionEnv(config=config)

    # ----- Baseline: evaluate random policy -----
    print("\n[1/3] Evaluating random baseline...")
    baseline = _quick_eval(env, n=50, policy=None)
    print(f"  Baseline success rate : {baseline['success_rate']:.1%}")
    print(f"  Baseline mean trauma  : {baseline['mean_trauma']:.4f}")

    # ----- Train with SB3 PPO -----
    print("\n[2/3] Training with PPO...")
    trainer = GoldfishPPOTrainer(
        NeedleInsertionEnv(config=config),
        tensorboard_log=os.path.join(output_dir, 'tb_logs'),
    )
    trainer.train(total_timesteps=total_timesteps)
    trainer.save(os.path.join(output_dir, 'trained_policy'))

    # ----- Evaluate trained policy -----
    print(f"\n[3/3] Evaluating trained policy ({eval_episodes} episodes)...")
    results = trainer.evaluate(n_episodes=eval_episodes)
    print(f"  Trained success rate  : {results['success_rate']:.1%}")
    print(f"  Trained mean trauma   : {results['mean_trauma']:.4f}")
    print(f"  Trained mean reward   : {results['mean_reward']:.1f}")

    # ----- Collect evidence log episodes -----
    print("\nCollecting evidence log episodes...")
    eval_env = NeedleInsertionEnv(config=config)
    evidence_episodes = []
    for ep_idx in range(min(50, eval_episodes)):
        obs, _ = eval_env.reset()
        done = False
        while not done:
            action = trainer.predict(obs, deterministic=True)
            obs, _, terminated, truncated, info = eval_env.step(action)
            done = terminated or truncated
        evidence_episodes.append({
            'episode_id': ep_idx,
            'success': info.get('success', False),
            'tissue_trauma': info.get('tissue_trauma', 0.),
            'vascular_proximity_mm': info.get('vascular_proximity_mm', 100.),
            'steps': eval_env.current_step,
        })

    # ----- Save evidence JSON -----
    evidence_path = os.path.join(output_dir, 'training_evidence.json')
    success_rates = [e['success'] for e in evidence_episodes]
    traumas       = [e['tissue_trauma'] for e in evidence_episodes]
    evidence_doc  = {
        'simulation_type': 'needle_insertion_v1',
        'physics_model': 'Kelvin-Voigt layered tissue (Okamura 2004)',
        'rl_algorithm': 'PPO (stable-baselines3)',
        'total_timesteps': total_timesteps,
        'baseline': baseline,
        'trained': results,
        'improvement': {
            'success_rate_delta': results['success_rate'] - baseline['success_rate'],
            'trauma_reduction':   baseline['mean_trauma'] - results['mean_trauma'],
        },
        'episodes': evidence_episodes,
        'summary': {
            'success_rate': float(np.mean(success_rates)),
            'mean_trauma':  float(np.mean(traumas)),
        },
        'validation_status': 'preclinical_simulation',
        'note': (
            'Results from simplified Kelvin-Voigt tissue mechanics. '
            'SOFA/PhysiCell/SimVascular integration is future work.'
        ),
    }
    with open(evidence_path, 'w') as f:
        json.dump(evidence_doc, f, indent=2)

    # ----- Training curves from SB3 monitor -----
    _plot_evaluation(baseline, results, output_dir)

    print("\n" + "=" * 60)
    print("Training complete!")
    print(f"  Success rate : {baseline['success_rate']:.1%} → {results['success_rate']:.1%}")
    print(f"  Trauma       : {baseline['mean_trauma']:.4f} → {results['mean_trauma']:.4f}")
    print(f"  Policy saved : {output_dir}/trained_policy.zip")
    print(f"  Evidence log : {evidence_path}")
    print("=" * 60)

    return evidence_doc


def _quick_eval(env, n: int = 50, policy=None) -> Dict:
    """Evaluate a policy (or random) for n episodes."""
    rewards, successes, traumas = [], [], []
    for _ in range(n):
        obs, _ = env.reset()
        ep_r, done = 0., False
        while not done:
            action = env.action_space.sample() if policy is None else policy(obs)
            obs, r, terminated, truncated, info = env.step(action)
            ep_r += r
            done  = terminated or truncated
        rewards.append(ep_r)
        successes.append(float(info.get('success', False)))
        traumas.append(float(info.get('tissue_trauma', 0.)))
    return {
        'success_rate': float(np.mean(successes)),
        'mean_reward':  float(np.mean(rewards)),
        'mean_trauma':  float(np.mean(traumas)),
    }


def _plot_evaluation(baseline: Dict, trained: Dict, output_dir: str):
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    fig.suptitle("Goldfish Needle Insertion v1 - Training Results", fontsize=13)

    ax = axes[0]
    labels  = ['Random\nbaseline', 'PPO trained']
    values  = [baseline['success_rate'] * 100, trained['success_rate'] * 100]
    colours = ['#d3d1c7', '#1D9E75']
    bars = ax.bar(labels, values, color=colours, width=0.5)
    ax.set_ylabel('Success rate (%)')
    ax.set_ylim(0, 100)
    ax.bar_label(bars, fmt='%.1f%%', padding=4)
    ax.set_title('Task success rate')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    ax = axes[1]
    values  = [baseline['mean_trauma'], trained['mean_trauma']]
    colours = ['#d3d1c7', '#1D9E75']
    bars = ax.bar(labels, values, color=colours, width=0.5)
    ax.set_ylabel('Mean cumulative trauma (0-1)')
    ax.axhline(y=0.20, color='#E24B4A', linestyle='--', linewidth=1, label='Damage threshold')
    ax.legend(fontsize=9)
    ax.bar_label(bars, fmt='%.4f', padding=4)
    ax.set_title('Tissue trauma score')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    path = os.path.join(output_dir, 'training_results.png')
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"Results plot saved: {path}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Goldfish Needle Insertion v1')
    parser.add_argument('--timesteps', type=int, default=300_000)
    parser.add_argument('--output',    type=str, default='./demo_output')
    parser.add_argument('--quick',     action='store_true',
                        help='Quick run: 30k timesteps (~2 min)')
    args = parser.parse_args()

    if args.quick:
        run_training(total_timesteps=30_000, output_dir='./quick_output')
    else:
        run_training(total_timesteps=args.timesteps, output_dir=args.output)
