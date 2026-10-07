"""Tests for Mesh Subsystem — NP-Hard Bridge and ApexGraphSwarm DAG."""

import unittest

from apex_audience_engine.mesh.graph_swarm import ApexGraphSwarmCoordinator, SwarmNodeStatus
from apex_audience_engine.mesh.np_hard_bridge import NPHardSwarmOptimizer, SwarmAllocationItem


class TestMesh(unittest.TestCase):

    def test_mckp_attention_budget_allocation(self) -> None:
        tribe_options = {
            "systems": [
                SwarmAllocationItem("systems", "low", value=10.0, cost_tokens=100),
                SwarmAllocationItem("systems", "deep", value=28.0, cost_tokens=300),
            ],
            "quant": [
                SwarmAllocationItem("quant", "low", value=12.0, cost_tokens=100),
                SwarmAllocationItem("quant", "deep", value=32.0, cost_tokens=350),
            ],
            "indie": [
                SwarmAllocationItem("indie", "low", value=8.0, cost_tokens=80),
                SwarmAllocationItem("indie", "deep", value=22.0, cost_tokens=200),
            ],
        }
        chosen, tot_val = NPHardSwarmOptimizer.solve_mckp_attention_budget(tribe_options, budget_limit=600)
        self.assertEqual(len(chosen), 3)
        self.assertLessEqual(sum(item.cost_tokens for item in chosen), 600)
        self.assertGreater(tot_val, 30.0)

    def test_influence_maximization_greedy(self) -> None:
        graph = {
            "A": ["B", "C"],
            "B": ["D"],
            "C": ["E"],
            "D": ["F"],
            "E": [],
            "F": [],
        }
        seeds = NPHardSwarmOptimizer.solve_influence_maximization(graph, k_seeds=2)
        self.assertIn("A", seeds)
        self.assertEqual(len(seeds), 2)

    def test_kemeny_young_consensus(self) -> None:
        candidates = ["F1", "F2", "F3"]
        rankings = [
            ["F1", "F2", "F3"],
            ["F1", "F3", "F2"],
            ["F2", "F1", "F3"],
        ]
        winner_order = NPHardSwarmOptimizer.solve_kemeny_young_consensus(candidates, rankings)
        self.assertEqual(winner_order[0], "F1")

    def test_graph_swarm_dag_execution(self) -> None:
        coordinator = ApexGraphSwarmCoordinator()
        coordinator.add_node("step1", lambda ctx: {"a": 10})
        coordinator.add_node("step2", lambda ctx: {"b": ctx["a"] * 2}, dependencies={"step1"})

        res = coordinator.execute_dag({"init": 0})
        self.assertEqual(res["a"], 10)
        self.assertEqual(res["b"], 20)
        self.assertEqual(coordinator.nodes["step2"].status, SwarmNodeStatus.COMPLETED)


if __name__ == "__main__":
    unittest.main()
