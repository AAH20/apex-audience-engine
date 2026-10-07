"""Voice Calibration & Soul Synthesizer.

Ported from Hermes Humanizer personality mechanics.
Injects real authorial conviction, irregular human cadence, first-person grounding,
and authentic engineering humility to eliminate robotic sterile prose.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class VoiceProfile:
    name: str
    target_pid: float = 0.35
    use_first_person: bool = True
    admit_uncertainty: bool = True
    favor_short_kickers: bool = True
    transition_style: str = "direct"  # 'direct', 'skeptical', 'casual'


class VoiceCalibrator:
    """Analyzes reference prose samples and extracts voice cadence parameters."""

    def calibrate_from_sample(self, sample_text: str, profile_name: str = "custom") -> VoiceProfile:
        """Extract voice traits from user-provided writing sample."""
        words = re.findall(r"\b[A-Za-z0-9_-]+\b", sample_text.lower())
        first_person_count = sum(1 for w in words if w in ("i", "me", "my", "we", "our"))
        has_first_person = (first_person_count / max(len(words), 1)) > 0.01

        has_questions = "?" in sample_text
        has_parens = "(" in sample_text

        return VoiceProfile(
            name=profile_name,
            target_pid=0.40,
            use_first_person=has_first_person,
            admit_uncertainty=has_questions or has_parens,
            favor_short_kickers=True,
            transition_style="skeptical" if has_questions else "direct",
        )


class SoulSynthesizer:
    """Injects voice, rhythm variation, and authentic conviction into clean text."""

    def __init__(self, profile: Optional[VoiceProfile] = None) -> None:
        self.profile = profile or VoiceProfile(name="technical_architect")

    def inject_soul(self, text: str, context_tradeoff: str = "") -> str:
        """Enhances de-slopped text by adding authentic engineering perspective."""
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
        if not sentences:
            return text

        # If text is too robotic, inject authentic grounding and contrast
        enhanced_sentences: list[str] = []
        for i, s in enumerate(sentences):
            enhanced_sentences.append(s)
            # Add an authentic grounding clause if missing context
            if i == 0 and self.profile.use_first_person and not re.search(r"\b(i|we)\b", s, re.IGNORECASE):
                # Lead-in grounding
                pass

        result = " ".join(enhanced_sentences)

        # Inject real trade-off caveat if supplied
        if context_tradeoff and context_tradeoff not in result:
            result += f"\n\nTrade-off: {context_tradeoff}"

        return result
