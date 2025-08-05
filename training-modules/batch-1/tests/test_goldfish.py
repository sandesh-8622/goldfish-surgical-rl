"""tests for goldfish env, cost module, agents, and evidence logger."""

import pytest


def test_env_resets():
    from goldfish.envs import NeedleInsertionEnv
    env = NeedleInsertionEnv()
    obs = env.reset()
    assert obs is not None
