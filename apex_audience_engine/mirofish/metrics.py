"""Metrics & Report Structures for MiroFish Synthetic Audience Simulation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from apex_audience_engine.mirofish.persona import EpistemicTribe


@dataclass
class PersonaReaction:
    persona_id: str
    tribe: EpistemicTribe
    resonance_score: float  # 0.0 to 1.0
    skepticism_score: float  # 0.0 to 1.0
    flame_war_risk: float  # 0.0 to 1.0
    verdict: str  # 'UPVOTE', 'STAR', 'DISMISS', 'CRITIQUE', 'FLAME'
    triggered_rejections: list[str] = field(default_factory=list)
    matched_acceptance: list[str] = field(default_factory=list)


@dataclass
class PreMortemReport:
    total_personas_simulated: int
    overall_receptivity_index: float  # RVI (Target > 1.5)
    flame_war_probability: float      # Target < 0.15
    upvote_velocity_score: float      # Projected early HN/Reddit upvote velocity
    tribe_resonance: dict[str, float]
    flagged_friction_points: list[str]
    prescriptive_recommendations: list[str]
    simulation_passed: bool
