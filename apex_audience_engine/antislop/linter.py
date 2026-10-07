"""Unified Anti-Slop Linter & Transformation Pipeline.

Performs multi-pass analysis, metric computation, linguistic de-slopification,
and soul injection. The primary entry point for anti-slop audience engineering.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from apex_audience_engine.antislop.entropy import EntropyCalculator, TextEntropyMetrics
from apex_audience_engine.antislop.heuristics import SlopHeuristicsEngine, SlopViolation
from apex_audience_engine.antislop.voice import SoulSynthesizer, VoiceCalibrator, VoiceProfile


@dataclass
class AntiSlopAuditResult:
    original_text: str
    cleaned_text: str
    violations: list[SlopViolation]
    original_metrics: TextEntropyMetrics
    cleaned_metrics: TextEntropyMetrics
    slop_reduction_pct: float
    audit_passed: bool


class AntiSlopEngine:
    """The master compiler for anti-slop copy auditing and authentic rewrite."""

    def __init__(self, profile: Optional[VoiceProfile] = None) -> None:
        self.heuristics = SlopHeuristicsEngine()
        self.entropy_calc = EntropyCalculator()
        self.calibrator = VoiceCalibrator()
        self.soul_synthesizer = SoulSynthesizer(profile)

    def process(self, text: str, voice_sample: Optional[str] = None, tradeoff_note: str = "") -> AntiSlopAuditResult:
        """Execute complete audit, de-slopification, and metric verification."""
        # 1. Audit original text
        violations = self.heuristics.audit(text)
        orig_metrics = self.entropy_calc.calculate(text, len(violations))

        # 2. Linguistic De-slopification pass
        deslopped_text, _ = self.heuristics.deslop(text)

        # 3. Optional Voice Calibration & Soul Injection pass
        if voice_sample:
            profile = self.calibrator.calibrate_from_sample(voice_sample)
            self.soul_synthesizer = SoulSynthesizer(profile)

        final_text = self.soul_synthesizer.inject_soul(deslopped_text, tradeoff_note)

        # 4. Measure cleaned metrics
        remaining_violations = self.heuristics.audit(final_text)
        cleaned_metrics = self.entropy_calc.calculate(final_text, len(remaining_violations))

        # Calculate slop reduction percentage
        if orig_metrics.slop_index > 0:
            reduction = max(0.0, (orig_metrics.slop_index - cleaned_metrics.slop_index) / orig_metrics.slop_index * 100)
        else:
            reduction = 0.0

        audit_passed = cleaned_metrics.slop_index <= 0.25 and cleaned_metrics.propositional_density >= 0.15

        return AntiSlopAuditResult(
            original_text=text,
            cleaned_text=final_text,
            violations=violations,
            original_metrics=orig_metrics,
            cleaned_metrics=cleaned_metrics,
            slop_reduction_pct=round(reduction, 2),
            audit_passed=audit_passed,
        )
