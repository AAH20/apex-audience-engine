"""Tests for Decisions Subsystem."""

import unittest

from apex_audience_engine.decisions.clef import CloudflareClefEngine, SlopSeverityTier
from apex_audience_engine.decisions.laya import LayaLocalRouter, TriageAction
from apex_audience_engine.decisions.router import DecisionHotPathRouter


class TestDecisions(unittest.TestCase):

    def setUp(self) -> None:
        self.clef = CloudflareClefEngine()
        self.laya = LayaLocalRouter()
        self.router = DecisionHotPathRouter()

    def test_clef_slop_severity_gating(self) -> None:
        clean_res = self.clef.evaluate_slop_gate("Clean text", slop_violation_count=0, pid=0.35)
        self.assertEqual(clean_res.selected_answer, SlopSeverityTier.CLEAN.value)
        self.assertGreater(clean_res.confidence, 0.80)

        slop_res = self.clef.evaluate_slop_gate("Bad text", slop_violation_count=8, pid=0.05)
        self.assertEqual(slop_res.selected_answer, SlopSeverityTier.TOXIC_HYPE.value)

    def test_laya_comment_triage(self) -> None:
        bug_res = self.laya.triage_comment("I got a TypeError traceback on line 42 when importing the solver")
        self.assertEqual(bug_res.action, TriageAction.HOTFIX_BUG)

        troll_res = self.laya.triage_comment("Just another scam money printer ai slop lol")
        self.assertEqual(troll_res.action, TriageAction.IGNORE_TROLL)

        tech_res = self.laya.triage_comment("How does the Clarke-Wright heuristic compare in latency to 2-opt?")
        self.assertEqual(tech_res.action, TriageAction.ENGAGE_TECHNICAL)

        amplify_res = self.laya.triage_comment("Brilliant engineering, starred and sharing with our team!")
        self.assertEqual(amplify_res.action, TriageAction.COMMUNITY_AMPLIFY)

    def test_router_selects_optimal_headline(self) -> None:
        candidates = [
            "A nice launch",
            "Show HN: Pure Python standard library solvers for supply chain bottlenecks",
            "Something random",
        ]
        res = self.router.select_optimal_headline(candidates, "pure python standard library zero deps")
        self.assertIn("Show HN", res.best_headline)
        self.assertEqual(res.evaluated_candidates_count, 3)


if __name__ == "__main__":
    unittest.main()
