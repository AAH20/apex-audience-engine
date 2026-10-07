"""Anti-Slop Heuristics — 34-Dimension AI Writing Pattern Linter & Normalizer.

Ported from WikiProject AI Cleanup, Hermes Humanizer, and empirical LLM slop corpora.
Detects, scores, and transforms AI-generated marketing, technical, and GTM prose into
high-signal, authentic, human-grounded technical narrative.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List, Pattern, Tuple


@dataclass(frozen=True)
class SlopViolation:
    rule_id: int
    rule_name: str
    matched_phrase: str
    suggested_replacement: str
    severity: float  # 0.0 to 1.0
    start_pos: int
    end_pos: int


# Dictionary of compile-ready pattern definitions
# Each tuple: (rule_id, rule_name, regex_pattern, suggested_replacement, severity)
SLOP_RULES_DATA: list[tuple[int, str, str, str, float]] = [
    # 1. Undue Emphasis on Significance & Legacy
    (
        1,
        "significance_inflation",
        r"\b(?:stands as|serves as)\s+(?:a\s+)?(?:testament|reminder|beacon)\b",
        "is proof of",
        0.9,
    ),
    (
        1,
        "significance_inflation",
        r"\b(?:a\s+)?(?:pivotal|vital|crucial)\s+(?:role|moment|turning point)\b",
        "an important shift",
        0.8,
    ),
    (
        1,
        "significance_inflation",
        r"\b(?:underscores|highlights)\s+its\s+(?:importance|significance)\b",
        "shows that",
        0.85,
    ),
    (
        1,
        "significance_inflation",
        r"\b(?:in\s+the\s+)?evolving\s+landscape\b",
        "in current development",
        0.75,
    ),
    (
        1,
        "significance_inflation",
        r"\bindelible\s+mark\b",
        "lasting impact",
        0.8,
    ),
    # 2. Undue Notability & Media Inflation
    (
        2,
        "notability_inflation",
        r"\bwritten\s+by\s+a\s+leading\s+expert\b",
        "written by",
        0.7,
    ),
    (
        2,
        "notability_inflation",
        r"\bmaintains\s+an\s+active\s+social\s+media\s+presence\b",
        "posts regularly on",
        0.6,
    ),
    # 3. Superficial -ing Participles
    (
        3,
        "superficial_participles",
        r",\s*(?:highlighting|underscoring|symbolizing|reflecting|fostering|showcasing)\s+",
        ", demonstrating ",
        0.7,
    ),
    # 4. Promotional Buzzwords & Figurative Overwriting
    (
        4,
        "promotional_buzzwords",
        r"\b(?:vibrant|groundbreaking|breathtaking|nestled\s+in|rich\s+tapestry)\b",
        "active",
        0.9,
    ),
    (
        4,
        "promotional_buzzwords",
        r"\bgame-changer\b",
        "step forward",
        0.85,
    ),
    # 5. Vague Attributions & Weasel Words
    (
        5,
        "vague_attributions",
        r"\b(?:industry\s+observers|observers\s+have\s+noted|experts\s+argue|some\s+critics\s+claim)\b",
        "engineers report",
        0.8,
    ),
    # 6. Formulaic Challenges & Future Outlook Framing
    (
        6,
        "formulaic_challenges",
        r"\bdespite\s+(?:these\s+)?challenges,\s*(?:the\s+)?(?:ecosystem|future|platform)\s+continues\s+to\s+thrive\b",
        "development continues",
        0.85,
    ),
    # 7. Overused High-Frequency AI Vocabulary
    (
        7,
        "overused_ai_vocab",
        r"\b(?:delve|delving|delves)\b",
        "examine",
        0.95,
    ),
    (
        7,
        "overused_ai_vocab",
        r"\bintricacies\b",
        "details",
        0.75,
    ),
    (
        7,
        "overused_ai_vocab",
        r"\binterplay\b",
        "interaction",
        0.7,
    ),
    (
        7,
        "overused_ai_vocab",
        r"\b(?:double\s+down|circle\s+back|deep\s+dive|lean\s+into|unpack)\b",
        "analyze",
        0.8,
    ),
    # 8. Copula Avoidance
    (
        8,
        "copula_avoidance",
        r"\b(?:serves\s+as|stands\s+as)\s+a\b",
        "is a",
        0.85,
    ),
    (
        8,
        "copula_avoidance",
        r"\b(?:boasts|features)\s+(?:a|an|over)\b",
        "has",
        0.75,
    ),
    # 9. Negative Parallelisms & Tailing Negations
    (
        9,
        "negative_parallelism",
        r"\bit['’]s\s+not\s+just\s+about\s+([^,]+),\s*it['’]s\s+about\s+",
        r"beyond \1, ",
        0.85,
    ),
    (
        9,
        "negative_parallelism",
        r",\s*no\s+(?:guessing|wasted\s+motion|surprises)\.?$",
        ".",
        0.8,
    ),
    # 10. Rule of Three Overuse
    (
        10,
        "rule_of_three",
        r"\b([A-Za-z]+),\s+([A-Za-z]+),\s+and\s+([A-Za-z]+)\s+(?:experiences|solutions|insights)\b",
        r"\1 and \2",
        0.7,
    ),
    # 12. False Ranges
    (
        12,
        "false_ranges",
        r"\bfrom\s+([A-Za-z\s]+)\s+to\s+([A-Za-z\s]+),\s+from\s+([A-Za-z\s]+)\s+to\s+([A-Za-z\s]+)\b",
        r"across \1 and \3",
        0.8,
    ),
    # 13. Passive Voice & Subjectless Fragments
    (
        13,
        "subjectless_fragments",
        r"\bno\s+configuration\s+file\s+needed\b",
        "You do not need a configuration file",
        0.65,
    ),
    # 14. Em Dash Overuse
    (
        14,
        "em_dash_overuse",
        r"—",
        " - ",
        0.6,
    ),
    # 18. Decorative Emojis in Technical Copy
    (
        18,
        "decorative_emojis",
        r"[🚀💡✅🔥⚡🎉✨]",
        "",
        0.85,
    ),
    # 20. Chatbot Artifacts & Correspondence Leftovers
    (
        20,
        "chatbot_artifacts",
        r"\b(?:i\s+hope\s+this\s+helps!|let\s+me\s+know\s+if\s+you['’]d\s+like|here\s+is\s+an\s+overview|certainly!|of\s+course!)\b",
        "",
        0.95,
    ),
    # 21. Knowledge Cutoff Disclaimers
    (
        21,
        "cutoff_disclaimers",
        r"\b(?:as\s+of\s+my\s+last\s+(?:training\s+)?update|based\s+on\s+available\s+information|while\s+specific\s+details\s+are\s+limited)\b",
        "",
        0.9,
    ),
    # 22. Sycophantic Servile Tone
    (
        22,
        "sycophancy",
        r"\b(?:great\s+question!|you['’]re\s+absolutely\s+right\b|that['’]s\s+an\s+excellent\s+point)\b",
        "",
        0.95,
    ),
    # 23. Filler Phrases
    (
        23,
        "filler_phrases",
        r"\bin\s+order\s+to\b",
        "to",
        0.75,
    ),
    (
        23,
        "filler_phrases",
        r"\bdue\s+to\s+the\s+fact\s+that\b",
        "because",
        0.8,
    ),
    (
        23,
        "filler_phrases",
        r"\bat\s+this\s+point\s+in\s+time\b",
        "currently",
        0.75,
    ),
    # 24. Excessive Hedging
    (
        24,
        "excessive_hedging",
        r"\bit\s+could\s+potentially\s+possibly\s+be\s+argued\b",
        "evidence suggests",
        0.85,
    ),
    # 25. Generic Positive Conclusion
    (
        25,
        "generic_positive_conclusion",
        r"\b(?:the\s+future\s+looks\s+bright|exciting\s+times\s+lie\s+ahead|journey\s+toward\s+excellence)\b",
        "active deployment continues",
        0.9,
    ),
    # 27. Persuasive Authority Tropes
    (
        27,
        "authority_tropes",
        r"\b(?:the\s+real\s+question\s+is|at\s+its\s+core|what\s+really\s+matters|the\s+heart\s+of\s+the\s+matter)\b",
        "specifically",
        0.8,
    ),
    # 28. Signposting & Tutorial Meta-Commentary
    (
        28,
        "signposting_announcements",
        r"\b(?:let['’]s\s+dive\s+in|let['’]s\s+explore|here['’]s\s+what\s+you\s+need\s+to\s+know|without\s+further\s+ado)\b",
        "",
        0.9,
    ),
    # 32. Rhetorical Question Self-Answer
    (
        32,
        "rhetorical_questions",
        r"\b(?:what\s+makes\s+an?\s+[A-Za-z]+\s+good\?\s*it\s+comes\s+down\s+to|ever\s+wondered\s+why|think\s+about\s+it:)\b",
        "A reliable system requires",
        0.85,
    ),
    # 33. Sentence Opener Tics
    (
        33,
        "opener_tics",
        r"^(?:So,|Look,|Interestingly,|Crucially,|Notably,)\s*",
        "",
        0.75,
    ),
    # 34. Reassurance Kickers
    (
        34,
        "reassurance_kickers",
        r"\b(?:and\s+that['’]s\s+okay\.|and\s+that['’]s\s+fine\.|you['’]re\s+not\s+alone\.|no\s+shame\s+in\s+that\.)\b",
        "",
        0.9,
    ),
]


class SlopHeuristicsEngine:
    """Compiled rule engine for high-speed AI slop auditing and normalization."""

    def __init__(self) -> None:
        self.rules: list[tuple[int, str, Pattern[str], str, float]] = [
            (rule_id, name, re.compile(pat, re.IGNORECASE | re.MULTILINE), repl, sev)
            for rule_id, name, pat, repl, sev in SLOP_RULES_DATA
        ]

    def audit(self, text: str) -> list[SlopViolation]:
        """Detect all slop violations in text."""
        violations: list[SlopViolation] = []
        for rule_id, name, pattern, repl, sev in self.rules:
            for match in pattern.finditer(text):
                violations.append(
                    SlopViolation(
                        rule_id=rule_id,
                        rule_name=name,
                        matched_phrase=match.group(0),
                        suggested_replacement=repl,
                        severity=sev,
                        start_pos=match.start(),
                        end_pos=match.end(),
                    )
                )
        return sorted(violations, key=lambda v: v.start_pos)

    def deslop(self, text: str) -> tuple[str, int]:
        """Applies automatic linguistic de-slopification rewrites.

        Returns (cleaned_text, replacement_count).
        """
        cleaned = text
        count = 0
        for _, _, pattern, repl, _ in self.rules:
            if pattern.search(cleaned):
                new_text, n = pattern.subn(repl, cleaned)
                if n > 0:
                    cleaned = new_text
                    count += n

        # Post-processing: clean double spaces, fix orphaned punctuation
        cleaned = re.sub(r"[ \t]+", " ", cleaned)
        cleaned = re.sub(r"\s+([,\.\?!])", r"\1", cleaned)
        cleaned = re.sub(r"\n\s*\n\s*\n+", "\n\n", cleaned)
        return cleaned.strip(), count
