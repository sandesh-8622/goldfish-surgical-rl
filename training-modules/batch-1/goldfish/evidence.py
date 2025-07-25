"""
goldfish.evidence

structured json logging for surgical training runs.
the format is intended to be compatible with what an FDA submission
would expect, but the V&V content has to come from real validation
studies which we don't have yet.
"""

import json
import time
from pathlib import Path


class EvidenceLogger:
    """append-only json log of training events and metrics."""

    def __init__(self, output_dir="./results", run_name=None):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        ts = time.strftime("%Y%m%d-%H%M%S")
        self.run_name = run_name or f"run-{ts}"
        self.log_path = self.output_dir / f"{self.run_name}_evidence.json"
        self.events = []


    def log_event(self, event_type, **kwargs):
        evt = {
            "timestamp": time.time(),
            "type": event_type,
            **kwargs,
        }
        self.events.append(evt)

    def log_step(self, step, obs, action, reward, cost_components):
        self.log_event(
            "step",
            step=int(step),
            reward=float(reward),
            cost=cost_components,
        )

    def log_episode_end(self, episode, total_reward, success, mean_trauma):
        self.log_event(
            "episode_end",
            episode=int(episode),
            total_reward=float(total_reward),
            success=bool(success),
            mean_trauma=float(mean_trauma),
        )

    def flush(self):
        with self.log_path.open("w", encoding="utf-8") as f:
            json.dump({"run": self.run_name, "events": self.events}, f, indent=2)
