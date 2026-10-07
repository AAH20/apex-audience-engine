"""Decision Hot-Path Router — Unified Cloudflare Clef & Laya Orchestrator."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from apex_audience_engine.decisions.clef import (
    ChannelFit,
    ClefDecisionResult,
    CloudflareClefEngine,
    SlopSeverityTier,
)
from apex_audience_engine.decisions.laya import LayaDecision, LayaLocalRouter, TriageAction


@dataclass
class HeadlineSelectionResult:
    best_headline: str
    target_channel: ChannelFit
    clef_decision: ClefDecisionResult
    evaluated_candidates_count: int


class DecisionHotPathRouter:
    """High-speed routing hub for launch assets and real-time community engagement."""

    def __init__(self) -> None:
        self.clef = CloudflareClefEngine()
        self.laya = LayaLocalRouter()

    def select_optimal_headline(
        self, candidate_headlines: list[str], body_text: str
    ) -> HeadlineSelectionResult:
        """Evaluates multiple headline candidates, picking the one with the highest front-page fit."""
        if not candidate_headlines:
            return HeadlineSelectionResult(
                best_headline="Show HN: Technical Launch",
                target_channel=ChannelFit.SHOW_HN,
                clef_decision=self.clef.evaluate_channel_fit("Show HN", body_text),
                evaluated_candidates_count=0,
            )

        scored: list[tuple[str, ClefDecisionResult]] = []
        for h in candidate_headlines:
            res = self.clef.evaluate_channel_fit(h, body_text)
            scored.append((h, res))

        # Sort by confidence
        scored.sort(key=lambda item: item[1].confidence, reverse=True)
        winner_headline, winner_decision = scored[0]

        return HeadlineSelectionResult(
            best_headline=winner_headline,
            target_channel=ChannelFit(winner_decision.selected_answer),
            clef_decision=winner_decision,
            evaluated_candidates_count=len(candidate_headlines),
        )

    def triage_incoming_comment(self, comment: str) -> LayaDecision:
        """Routes an incoming comment via Laya System 1 decision engine."""
        return self.laya.triage_comment(comment)
