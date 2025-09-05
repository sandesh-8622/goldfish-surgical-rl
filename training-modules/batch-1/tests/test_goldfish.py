"""
Goldfish Test Suite

Tests validate BEHAVIOUR, not just tensor shapes.
Each test has a comment explaining what it checks and why it matters.
"""

import numpy as np
import pytest
import torch


# =========================================================================== #
#  Environment tests                                                           #
# =========================================================================== #

class TestNeedleInsertionEnv:

    def _make_env(self):
        from goldfish.envs import NeedleInsertionEnv, NeedleInsertionConfig
        cfg = NeedleInsertionConfig(tissue_size=(32, 32, 32), max_steps=100)
        return NeedleInsertionEnv(config=cfg)

    def test_observation_shape(self):
        """Obs must be the documented 15-dim vector."""
        env = self._make_env()
        obs, _ = env.reset()
        assert obs.shape == (15,), f"Expected (15,) got {obs.shape}"

    def test_observation_dtype(self):
        """SB3 requires float32 observations."""
        env = self._make_env()
        obs, _ = env.reset()
        assert obs.dtype == np.float32

    def test_action_space(self):
        """Action must be 6-dim in [-1, 1]."""
        env = self._make_env()
        assert env.action_space.shape == (6,)
        assert env.action_space.low[0]  == -1.0
        assert env.action_space.high[0] ==  1.0

    def test_observation_bounds(self):
        """
        Several obs components must be in [0,1] by design:
          indices 0-2 (position normalised), 10 (strain), 11 (force),
          12 (vascular), 13 (trauma), 14 (time_left).
        """
        env = self._make_env()
        env.reset()
        for _ in range(30):
            obs, _, done, _, _ = env.step(env.action_space.sample())
            for idx in [0, 1, 2, 10, 11, 12, 13, 14]:
                assert -0.05 <= obs[idx] <= 1.05, \
                    f"obs[{idx}] = {obs[idx]:.4f} out of expected [0,1] range"
            if done:
                env.reset()

    def test_step_returns_correct_types(self):
        env = self._make_env()
        env.reset()
        obs, reward, terminated, truncated, info = env.step(env.action_space.sample())
        assert isinstance(obs,       np.ndarray)
        assert isinstance(reward,    float)
        assert isinstance(terminated, bool)
        assert isinstance(truncated,  bool)
        assert isinstance(info,      dict)

    def test_success_terminates_episode(self):
        """If needle reaches target, terminated must be True."""
        env = self._make_env()
        env.reset()
        # Teleport needle to target
        env.needle_position = env.target_position.copy()
        _, _, terminated, _, info = env.step(np.zeros(6))
        assert terminated
        assert info['success']

    def test_max_steps_truncation(self):
        """Episode must end at max_steps if target never reached."""
        env = self._make_env()
        env.reset()
        done = False
        steps = 0
        while not done:
            _, _, terminated, truncated, _ = env.step(np.zeros(6))
            done = terminated or truncated
            steps += 1
        assert steps <= env.config.max_steps + 1

    def test_trauma_only_increases(self):
        """Cumulative trauma must be monotonically non-decreasing."""
        env = self._make_env()
        env.reset()
        prev_trauma = 0.0
        for _ in range(50):
            obs, _, done, _, _ = env.step(env.action_space.sample())
            trauma = float(obs[13])
            assert trauma >= prev_trauma - 1e-6, \
                f"Trauma decreased: {prev_trauma:.6f} -> {trauma:.6f}"
            prev_trauma = trauma
            if done:
                break

    def test_moving_toward_target_gives_positive_reward(self):
        """
        A move that halves the distance to target should yield positive reward
        (or at least better than a move that doubles the distance).
        """
        env = self._make_env()
        env.reset()
        # Measure reward for zero action (no movement)
        _, r_zero, _, _, _ = env.step(np.zeros(6))

        env.reset()
        # Force a direct move toward target
        tgt = env.target_position
        pos = env.needle_position
        direction = (tgt - pos)
        direction /= (np.linalg.norm(direction) + 1e-8)
        _, r_toward, _, _, _ = env.step(
            np.clip(np.concatenate([direction, [0, 0, 0]]), -1, 1).astype(np.float32)
        )
        assert r_toward >= r_zero, (
            f"Moving toward target ({r_toward:.2f}) should reward >= no move ({r_zero:.2f})"
        )

    def test_gym_api_compatibility(self):
        """stable-baselines3 env checker - catches API violations."""
        try:
            from stable_baselines3.common.env_checker import check_env
            env = self._make_env()
            check_env(env, warn=True, skip_render_check=True)
        except ImportError:
            pytest.skip("stable-baselines3 not installed")


# =========================================================================== #
#  Physics tests                                                               #
# =========================================================================== #

class TestLayeredTissue:

    def _make_sim(self):
        from goldfish.envs import LayeredTissueSimulator
        return LayeredTissueSimulator(tissue_size=(64, 64, 64))

    def test_tissue_type_layers(self):
        """Tissue types must match layer boundaries."""
        sim = self._make_sim()
        name_s, _ = sim.tissue_type(1.0)
        name_m, _ = sim.tissue_type(sim.soft_end + 5)
        name_f, _ = sim.tissue_type(sim.muscle_end + 5)
        assert name_s == 'soft'
        assert name_m == 'muscle'
        assert name_f == 'fat'

    def test_insertion_force_increases_with_depth(self):
        """Deeper needle → higher insertion force (for same tissue layer)."""
        sim = self._make_sim()
        pos_shallow = np.array([32., 32., 2.])
        pos_deep    = np.array([32., 32., 10.])
        f_shallow = sim.insertion_force(pos_shallow, velocity_z=1.0)
        f_deep    = sim.insertion_force(pos_deep,    velocity_z=1.0)
        assert f_deep > f_shallow, \
            f"Deeper force {f_deep:.4f} should > shallow {f_shallow:.4f}"

    def test_insertion_force_nonnegative(self):
        """Force cannot be negative."""
        sim = self._make_sim()
        for z in np.linspace(0, 63, 10):
            pos = np.array([32., 32., z])
            f = sim.insertion_force(pos, velocity_z=0.)
            assert f >= 0., f"Negative force at z={z}: {f}"

    def test_strain_nonnegative_and_bounded(self):
        """Strain must be in [0, 1] everywhere."""
        sim = self._make_sim()
        for z in np.linspace(0, 63, 20):
            s = sim.strain_at_tip(np.array([32., 32., z]))
            assert 0. <= s <= 1., f"Strain {s:.4f} out of [0,1] at z={z}"

    def test_muscle_stiffer_than_fat(self):
        """Muscle tissue must generate more resistance than fat."""
        sim = self._make_sim()
        pos_muscle = np.array([32., 32., float(sim.soft_end + 5)])
        pos_fat    = np.array([32., 32., float(sim.muscle_end + 5)])
        # Both at same depth-into-layer offset
        f_muscle = sim.insertion_force(pos_muscle, velocity_z=2.0)
        f_fat    = sim.insertion_force(pos_fat,    velocity_z=2.0)
        assert f_muscle > f_fat, \
            f"Muscle ({f_muscle:.4f} N) should be stiffer than fat ({f_fat:.4f} N)"

    def test_vascular_proximity_decreases_near_vessel(self):
        """Moving the needle closer to a vessel must decrease proximity distance."""
        sim = self._make_sim()
        if len(sim.vessels) == 0:
            pytest.skip("No vessels generated")
        # Find a vessel
        vessel = sim.vessels[0]
        vx, vy, vz = vessel[:3]
        far_pos   = np.array([vx, vy, vz - 20.0])
        close_pos = np.array([vx, vy, vz - 5.0])
        d_far   = sim.vascular_proximity(far_pos)
        d_close = sim.vascular_proximity(close_pos)
        assert d_close < d_far, \
            f"Closer pos ({d_close:.2f} mm) should be smaller than far ({d_far:.2f} mm)"


# =========================================================================== #
#  Cost module tests                                                           #
# =========================================================================== #

class TestCostModule:

    def _make_costs(self):
        from goldfish.cost_module import TissueTraumaCost, VascularProximityCost
        return TissueTraumaCost(), VascularProximityCost()

    def test_zero_strain_zero_cost(self):
        """No strain → no trauma cost."""
        tc, _ = self._make_costs()
        strain = torch.zeros(4)
        force  = torch.zeros(4)
        cost, _ = tc(strain, force)
        assert cost.item() < 1e-6, f"Expected ~0 cost for zero strain, got {cost.item()}"

    def test_excess_strain_penalised(self):
        """Strain above MAX_TISSUE_STRAIN (0.20) must incur positive cost."""
        from goldfish.cost_module import BiologicalThresholds
        tc, _ = self._make_costs()
        strain = torch.full((4,), BiologicalThresholds.MAX_TISSUE_STRAIN + 0.10)
        force  = torch.zeros(4)
        cost, _ = tc(strain, force)
        assert cost.item() > 0., "High strain should produce positive cost"

    def test_vascular_safe_distance_no_penalty(self):
        """Needle >= MIN_VASCULAR_DISTANCE_MM from vessel → zero vascular cost."""
        from goldfish.cost_module import BiologicalThresholds
        _, vc = self._make_costs()
        safe_dist = torch.full((4,), BiologicalThresholds.MIN_VASCULAR_DISTANCE_MM + 1.)
        cost, _   = vc(safe_dist)
        assert cost.item() < 1e-6, \
            f"Safe distance should yield ~0 cost, got {cost.item():.6f}"

    def test_vascular_violation_penalised(self):
        """Needle inside MIN_VASCULAR_DISTANCE_MM → positive cost."""
        _, vc = self._make_costs()
        unsafe_dist = torch.zeros(4)   # touching the vessel
        cost, _     = vc(unsafe_dist)
        assert cost.item() > 0., "Vessel contact should produce positive cost"

    def test_cost_monotone_with_strain(self):
        """Higher strain must produce higher or equal cost."""
        tc, _ = self._make_costs()
        costs = []
        for s in [0.0, 0.10, 0.20, 0.30, 0.40]:
            strain = torch.full((4,), s)
            c, _   = tc(strain, torch.zeros(4))
            costs.append(c.item())
        for i in range(len(costs) - 1):
            assert costs[i] <= costs[i+1] + 1e-6, \
                f"Cost not monotone: costs[{i}]={costs[i]:.6f} > costs[{i+1}]={costs[i+1]:.6f}"

    def test_insertion_score_range(self):
        """compute_needle_insertion_score must return values in [0, 1]."""
        from goldfish.cost_module import compute_needle_insertion_score
        score = compute_needle_insertion_score(50., 48., 2., 0.1, 5., 12.)
        for k, v in score.items():
            assert 0. <= v <= 1. + 1e-6, f"Score '{k}' = {v:.4f} outside [0,1]"

    def test_perfect_insertion_scores_high(self):
        """
        Depth error=0, lateral=0, no trauma, safe vascular margin, fast → near 1.0.
        """
        from goldfish.cost_module import compute_needle_insertion_score, BiologicalThresholds
        score = compute_needle_insertion_score(
            target_depth=50., actual_depth=50., lateral_error=0.,
            tissue_trauma=0., vascular_proximity_mm=10., time_to_complete=5.,
        )
        assert score['total_score'] > 0.85, \
            f"Perfect insertion should score >0.85, got {score['total_score']:.4f}"


# =========================================================================== #
#  World model tests                                                           #
# =========================================================================== #

class TestSimulationWorldModel:

    def test_output_shape(self):
        """SimulationWorldModel must output (B, obs_dim) tensor."""
        from goldfish.world_model import SimulationWorldModel
        m = SimulationWorldModel(obs_dim=15, action_dim=6)
        obs = torch.randn(4, 15)
        act = torch.randn(4, 6)
        out = m(obs, act)
        assert out.shape == (4, 15), f"Expected (4,15) got {out.shape}"

    def test_residual_structure(self):
        """With zero net output the model should return obs unchanged."""
        from goldfish.world_model import SimulationWorldModel
        m = SimulationWorldModel(obs_dim=15, action_dim=6)
        # Zero-out all weights → net(x) = 0 → output = obs + 0 = obs
        for p in m.net.parameters():
            p.data.zero_()
        obs = torch.randn(2, 15)
        act = torch.randn(2, 6)
        out = m(obs, act)
        assert torch.allclose(out, obs, atol=1e-5), "Residual structure broken"


# =========================================================================== #
#  Agent tests                                                                 #
# =========================================================================== #

class TestRLAgent:

    def test_predict_shape(self):
        """RLAgent.predict must return a (6,) action."""
        from goldfish.agents import RLAgent
        agent = RLAgent(obs_dim=15, action_dim=6)
        action = agent.predict(np.random.randn(15).astype(np.float32))
        assert action.shape == (6,), f"Expected (6,) got {action.shape}"

    def test_train_step_improves_after_enough_data(self):
        """
        Train step must run without error given enough data.
        We do NOT assert loss value because we'd need to run many steps - just
        assert the step completes and returns a valid dict.
        """
        from goldfish.agents import RLAgent
        agent = RLAgent(obs_dim=15, action_dim=6)
        for _ in range(100):
            agent.update({
                'observation':      np.random.randn(15).astype(np.float32),
                'action':           np.random.randn(6).astype(np.float32),
                'reward':           float(np.random.randn()),
                'next_observation': np.random.randn(15).astype(np.float32),
                'done':             False,
            })
        metrics = agent.train_step(batch_size=64)
        assert 'policy_loss' in metrics
        assert 'value_loss'  in metrics
        assert np.isfinite(metrics['policy_loss'])


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
