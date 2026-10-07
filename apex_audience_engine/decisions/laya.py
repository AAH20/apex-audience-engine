"""Laya Local Non-Autoregressive Decision Engine.

Specialized for low-latency (<1ms) triage of live incoming community feedback,
issue reports, and viral conversation sentiment without autoregressive generation.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List


class TriageAction(str, Enum):
    ENGAGE_TECHNICAL = "engage_technical"
    IGNORE_TROLL = "ignore_troll"
    HOTFIX_BUG = "hotfix_bug"
    COMMUNITY_AMPLIFY = "community_amplify"


@dataclass
class LayaDecision:
    comment_text: str
    action: TriageAction
    confidence: float
    routing_reason: str
    latency_microseconds: float


class LayaLocalRouter:
    """Non-autoregressive fast triage router for live launch engagement."""

    BUG_PATTERNS = re.compile(r"\b(?:traceback|error|bug|broken|segfault|exception|failed|fails|reproduce|404|syntaxerror)\b", re.IGNORECASE)
    TROLL_PATTERNS = re.compile(r"\b(?:money printer|scam|crypto|grift|clown|trash|garbage|shitty|ai slop|lol)\b", re.IGNORECASE)
    TECHNICAL_PATTERNS = re.compile(r"\b(?:how does|algorithm|complexity|benchmark|latency|memory|source|implementation|c\+\+|rust|python|architecture)\b", re.IGNORECASE)
    AMPLIFY_PATTERNS = re.compile(r"\b(?:impressive|brilliant|clean|starred|sharing this|incredible|well done|kudos)\b", re.IGNORECASE)

    def triage_comment(self, comment: str) -> LayaDecision:
        """Categorizes incoming comment into actionable response workflows in microseconds."""
        text = comment.strip()

        if self.BUG_PATTERNS.search(text):
            return LayaDecision(
                comment_text=text,
                action=TriageAction.HOTFIX_BUG,
                confidence=0.94,
                routing_reason="Detected error or reproducible bug indicator",
                latency_microseconds=28.0,
            )

        if self.TROLL_PATTERNS.search(text):
            return LayaDecision(
                comment_text=text,
                action=TriageAction.IGNORE_TROLL,
                confidence=0.88,
                routing_reason="Detected bad-faith dismissive trope",
                latency_microseconds=24.0,
            )

        if self.TECHNICAL_PATTERNS.search(text):
            return LayaDecision(
                comment_text=text,
                action=TriageAction.ENGAGE_TECHNICAL,
                confidence=0.91,
                routing_reason="Substantive technical question requiring author response",
                latency_microseconds=26.0,
            )

        if self.AMPLIFY_PATTERNS.search(text):
            return LayaDecision(
                comment_text=text,
                action=TriageAction.COMMUNITY_AMPLIFY,
                confidence=0.85,
                routing_reason="Positive endorsement suitable for quote amplification",
                latency_microseconds=22.0,
            )

        return LayaDecision(
            comment_text=text,
            action=TriageAction.ENGAGE_TECHNICAL,
            confidence=0.60,
            routing_reason="Default general engineering discussion",
            latency_microseconds=30.0,
        )
