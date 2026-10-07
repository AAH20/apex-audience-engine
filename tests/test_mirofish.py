"""Tests for MiroFish Synthetic Audience Subsystem."""

import unittest

from apex_audience_engine.mirofish.persona import EpistemicTribe, PersonaFactory
from apex_audience_engine.mirofish.simulator import MiroFishSwarmSimulator


class TestMiroFish(unittest.TestCase):

    def setUp(self) -> None:
        self.simulator = MiroFishSwarmSimulator()

    def test_default_swarm_coverage(self) -> None:
        swarm = PersonaFactory.create_default_swarm(size_per_tribe=3)
        self.assertEqual(len(swarm), 15)
        tribes = {p.tribe for p in swarm}
        self.assertEqual(len(tribes), 5)

    def test_rejection_trigger_increases_skepticism(self) -> None:
        # Heavily hyped draft triggering rejection triggers
        hyped_headline = "A revolutionary game-changer that will delve into miracle algorithms"
        hyped_body = "Guaranteed profit with money printer magic and passive income."

        report = self.simulator.simulate_launch(
            headline=hyped_headline,
            body_text=hyped_body,
            benchmark_claim="",
            has_reproducible_code=False,
        )
        self.assertGreater(report.flame_war_probability, 0.20)
        self.assertLess(report.overall_receptivity_index, 1.0)
        self.assertFalse(report.simulation_passed)
        self.assertGreater(len(report.flagged_friction_points), 0)

    def test_pure_technical_copy_passes_simulation(self) -> None:
        technical_headline = "Show HN: Zero-dependency pure Python solvers for 8 NP-hard supply chain bottlenecks"
        technical_body = "Built entirely with Python 3.10 standard library. Microsecond deterministic execution with full benchmarks."

        report = self.simulator.simulate_launch(
            headline=technical_headline,
            body_text=technical_body,
            benchmark_claim="p50=1.03ms across all 8 engines",
            has_reproducible_code=True,
        )
        self.assertGreater(report.overall_receptivity_index, 1.20)
        self.assertLess(report.flame_war_probability, 0.10)
        self.assertTrue(report.simulation_passed)


if __name__ == "__main__":
    unittest.main()
