"""Anti-Slop Subsystem — 34-rule Linter, Entropy Scoring, and Soul Synthesizer."""

from apex_audience_engine.antislop.entropy import EntropyCalculator, TextEntropyMetrics
from apex_audience_engine.antislop.heuristics import SlopHeuristicsEngine, SlopViolation
from apex_audience_engine.antislop.linter import AntiSlopAuditResult, AntiSlopEngine
from apex_audience_engine.antislop.voice import SoulSynthesizer, VoiceCalibrator, VoiceProfile

__all__ = [
    "AntiSlopEngine",
    "AntiSlopAuditResult",
    "SlopHeuristicsEngine",
    "SlopViolation",
    "EntropyCalculator",
    "TextEntropyMetrics",
    "VoiceCalibrator",
    "SoulSynthesizer",
    "VoiceProfile",
]
