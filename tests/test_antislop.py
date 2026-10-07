"""Tests for Anti-Slop Subsystem."""

import unittest

from apex_audience_engine.antislop.entropy import EntropyCalculator
from apex_audience_engine.antislop.heuristics import SlopHeuristicsEngine
from apex_audience_engine.antislop.linter import AntiSlopEngine
from apex_audience_engine.antislop.voice import VoiceCalibrator, VoiceProfile


class TestAntiSlop(unittest.TestCase):

    def setUp(self) -> None:
        self.heuristics = SlopHeuristicsEngine()
        self.entropy = EntropyCalculator()
        self.engine = AntiSlopEngine()

    def test_detects_significance_inflation(self) -> None:
        text = "This stands as a testament to the evolving landscape and marks a pivotal moment."
        violations = self.heuristics.audit(text)
        self.assertTrue(any(v.rule_name == "significance_inflation" for v in violations))

    def test_detects_overused_ai_vocabulary(self) -> None:
        text = "Let us delve into the intricacies of this game-changer."
        violations = self.heuristics.audit(text)
        matched_rules = {v.rule_name for v in violations}
        self.assertIn("overused_ai_vocab", matched_rules)
        self.assertIn("promotional_buzzwords", matched_rules)

    def test_deslop_removes_fluff(self) -> None:
        raw = "In order to succeed, let's dive in and delve into the code!"
        cleaned, count = self.heuristics.deslop(raw)
        self.assertGreater(count, 0)
        self.assertNotIn("delve", cleaned.lower())
        self.assertNotIn("let's dive in", cleaned.lower())

    def test_entropy_and_propositional_density(self) -> None:
        technical_text = (
            "The VRPTW solver executed in 237.58 µs with 12 customers, achieving 4209 ops/sec. "
            "Memory remained bounded at 4.2 MB across 1000 iterations."
        )
        metrics = self.entropy.calculate(technical_text, slop_violation_count=0)
        self.assertGreater(metrics.propositional_density, 0.20)
        self.assertLess(metrics.slop_index, 0.25)
        self.assertTrue(metrics.is_high_signal)

    def test_full_pipeline_audit_pass(self) -> None:
        ai_heavy = (
            "This incredible tool serves as a beacon of innovation in today's rapidly evolving landscape, "
            "underscoring its vital role. What makes it good? It comes down to speed."
        )
        res = self.engine.process(ai_heavy)
        self.assertGreater(res.slop_reduction_pct, 10.0)
        self.assertNotIn("serves as a beacon", res.cleaned_text.lower())


if __name__ == "__main__":
    unittest.main()
