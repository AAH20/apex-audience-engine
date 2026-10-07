"""Information Entropy & Propositional Density Metrics.

Quantifies information density, stylometric burstiness, and the Slop Index (S_slop)
to mathematically distinguish high-signal human engineering prose from empty AI fluff.
"""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass


@dataclass(frozen=True)
class TextEntropyMetrics:
    word_count: int
    sentence_count: int
    mean_sentence_length: float
    sentence_length_std_dev: float  # Burstiness indicator
    shannon_entropy: float
    propositional_density: float  # Facts / Total Words (Target >= 0.35)
    slop_index: float  # 0.0 (Pure Signal) to 1.0 (Pure AI Slop)
    is_high_signal: bool


class EntropyCalculator:
    """Computes mathematical stylometric metrics and information density."""

    # Patterns indicating concrete empirical facts: numbers, code tokens, units, metrics
    EMPIRICAL_FACT_REGEX = re.compile(
        r"(?:\b\d+(?:\.\d+)?(?:%|ms|µs|ns|s|m|km|MB|GB|TB|KB|ops/sec|kg|t|nm|dB)?\b|"
        r"\b(?:O\(|v\d+\.\d+|https?://|git\s+|pip\s+|cargo\s+|docker\s+|def\s+|class\s+|SELECT\s+)|"
        r"`[^`]+`|\b[A-Za-z0-9_]+\.[a-z]{1,4}\b)",
        re.IGNORECASE,
    )

    def calculate(self, text: str, slop_violation_count: int = 0) -> TextEntropyMetrics:
        """Calculate full entropy and signal density for given text."""
        words = re.findall(r"\b[A-Za-z0-9_-]+\b", text.lower())
        word_count = len(words)

        if word_count == 0:
            return TextEntropyMetrics(
                word_count=0,
                sentence_count=0,
                mean_sentence_length=0.0,
                sentence_length_std_dev=0.0,
                shannon_entropy=0.0,
                propositional_density=0.0,
                slop_index=1.0,
                is_high_signal=False,
            )

        # Sentence segmentation
        raw_sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]
        sentence_count = max(len(raw_sentences), 1)

        sentence_lengths = [len(re.findall(r"\b[A-Za-z0-9_-]+\b", s)) for s in raw_sentences]
        mean_len = sum(sentence_lengths) / sentence_count

        # Variance & Std Dev of sentence length (Human burstiness measure)
        if sentence_count > 1:
            variance = sum((l - mean_len) ** 2 for l in sentence_lengths) / (sentence_count - 1)
            std_dev = math.sqrt(variance)
        else:
            std_dev = 0.0

        # Shannon Entropy H = - sum(p * log2(p))
        counts = Counter(words)
        shannon = -sum((c / word_count) * math.log2(c / word_count) for c in counts.values())

        # Propositional Density = Empirical Facts count / Total Words
        facts = self.EMPIRICAL_FACT_REGEX.findall(text)
        fact_count = len(facts)
        pid = min(fact_count / word_count, 1.0) if word_count > 0 else 0.0

        # Slop Index formulation:
        # Penalties:
        # - High slop violation density (violations / word_count)
        # - Low sentence length variance (std_dev < 4.0 indicates robotic rhythm)
        # - Low propositional density (pid < 0.15)
        # Bonuses:
        # - High propositional density (pid >= 0.30)
        # - Natural sentence burstiness (std_dev >= 8.0)
        violation_density = (slop_violation_count * 10) / word_count
        burstiness_penalty = max(0.0, (6.0 - std_dev) / 6.0) if std_dev < 6.0 else 0.0
        pid_deficit = max(0.0, (0.30 - pid) / 0.30)

        slop_score = (0.50 * min(violation_density, 1.0)) + (0.30 * pid_deficit) + (0.20 * burstiness_penalty)
        slop_score = max(0.0, min(slop_score, 1.0))

        is_high_signal = slop_score < 0.25 and pid >= 0.20

        return TextEntropyMetrics(
            word_count=word_count,
            sentence_count=sentence_count,
            mean_sentence_length=round(mean_len, 2),
            sentence_length_std_dev=round(std_dev, 2),
            shannon_entropy=round(shannon, 3),
            propositional_density=round(pid, 3),
            slop_index=round(slop_score, 3),
            is_high_signal=is_high_signal,
        )
