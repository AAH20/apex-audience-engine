"""MiroFish Synthetic Audience Multi-Agent Swarm Simulator.

Simulates crowd reactions, developer flame-wars, and viral reception before public launch.
Pressure-tests headlines, copy, benchmarks, and claims across simulated technical personas.
"""

from __future__ import annotations

import re
from typing import List, Optional

from apex_audience_engine.mirofish.metrics import PersonaReaction, PreMortemReport
from apex_audience_engine.mirofish.persona import EpistemicTribe, PersonaFactory, SyntheticPersona


class MiroFishSwarmSimulator:
    """Multi-agent simulator for technical product pre-mortems."""

    def __init__(self, personas: Optional[list[SyntheticPersona]] = None) -> None:
        self.personas = personas or PersonaFactory.create_default_swarm(size_per_tribe=5)

    def simulate_launch(
        self,
        headline: str,
        body_text: str,
        benchmark_claim: str = "",
        has_reproducible_code: bool = True,
    ) -> PreMortemReport:
        """Runs multi-round pre-mortem simulation against the persona swarm."""
        full_content = f"{headline} {body_text} {benchmark_claim}".lower()
        reactions: list[PersonaReaction] = []

        total_resonance = 0.0
        total_skepticism = 0.0
        total_flame_risk = 0.0

        tribe_resonance_sums: dict[str, float] = {t.value: 0.0 for t in EpistemicTribe}
        tribe_counts: dict[str, int] = {t.value: 0 for t in EpistemicTribe}

        friction_points: set[str] = set()

        # Normalize text and hyphens for flexible token matching
        normalized_content = f"{full_content} {full_content.replace('-', ' ')}"

        for p in self.personas:
            # Check rejection triggers
            triggered = [trig for trig in p.rejection_triggers if trig in full_content or trig in normalized_content]
            # Check acceptance drivers
            matched = [drv for drv in p.acceptance_drivers if drv in full_content or drv in normalized_content]

            # Base scores
            skepticism = p.base_skepticism
            if triggered:
                skepticism = min(1.0, skepticism + 0.20 * len(triggered))
                for trig in triggered:
                    friction_points.add(f"Tribe '{p.tribe.value}' flagged rejection trigger: '{trig}'")

            if matched:
                skepticism = max(0.08, skepticism - 0.28 * len(matched))

            if not has_reproducible_code and p.tribe in (EpistemicTribe.SYSTEMS_ENGINEER, EpistemicTribe.QUANT_RESEARCHER):
                skepticism = min(1.0, skepticism + 0.35)
                friction_points.add("Missing verifiable code/benchmarks triggered severe engineer skepticism")

            # Resonance score
            resonance = max(0.0, 1.0 - skepticism)
            if matched and not triggered:
                resonance = min(1.0, resonance + 0.30 * len(matched))

            # Flame-war risk: occurs when high skepticism coincides with strong rejection triggers
            flame_risk = 0.0
            if triggered and skepticism > 0.70:
                flame_risk = min(1.0, (skepticism - 0.5) * 1.8)

            # Verdict determination
            if flame_risk > 0.5:
                verdict = "FLAME"
            elif resonance > 0.70:
                verdict = "STAR"
            elif resonance > 0.45:
                verdict = "UPVOTE"
            elif skepticism > 0.65:
                verdict = "CRITIQUE"
            else:
                verdict = "DISMISS"

            rx = PersonaReaction(
                persona_id=p.id,
                tribe=p.tribe,
                resonance_score=round(resonance, 3),
                skepticism_score=round(skepticism, 3),
                flame_war_risk=round(flame_risk, 3),
                verdict=verdict,
                triggered_rejections=triggered,
                matched_acceptance=matched,
            )
            reactions.append(rx)

            # Accumulate weighted totals
            w = p.influence_weight
            total_resonance += resonance * w
            total_skepticism += skepticism * w
            total_flame_risk += flame_risk * w

            tribe_resonance_sums[p.tribe.value] += resonance
            tribe_counts[p.tribe.value] += 1

        # RVI = (Total Weighted Resonance) / (Total Weighted Skepticism + epsilon)
        rvi = total_resonance / max(total_skepticism, 0.01)
        flame_prob = total_flame_risk / max(len(self.personas), 1)

        tribe_averages = {
            tribe: round(tribe_resonance_sums[tribe] / max(tribe_counts[tribe], 1), 3)
            for tribe in tribe_resonance_sums
        }

        # Recommendations based on simulation findings
        recommendations: list[str] = []
        if flame_prob > 0.15:
            recommendations.append("HIGH FLAME-WAR RISK: Strip all hyperbole and unsupported benchmark claims.")
        if tribe_averages.get("systems_engineer", 0) < 0.5:
            recommendations.append("Emphasize zero-dependency pure Python/C++/Rust mechanics and memory benchmarks.")
        if tribe_averages.get("quant_researcher", 0) < 0.5:
            recommendations.append("Explicitly include mathematical bounds (e.g. KaTeX equations, O(N) notation).")
        if tribe_averages.get("indie_hacker", 0) < 0.5:
            recommendations.append("Highlight 1-line installation simplicity and instant time-to-value.")

        if not recommendations:
            recommendations.append("Swarm consensus is overwhelmingly positive; launch materials primed for front-page velocity.")

        simulation_passed = rvi >= 1.20 and flame_prob < 0.20

        return PreMortemReport(
            total_personas_simulated=len(self.personas),
            overall_receptivity_index=round(rvi, 3),
            flame_war_probability=round(flame_prob, 3),
            upvote_velocity_score=round(min(1.0, total_resonance / (len(self.personas) * 1.5)), 3),
            tribe_resonance=tribe_averages,
            flagged_friction_points=sorted(list(friction_points)),
            prescriptive_recommendations=recommendations,
            simulation_passed=simulation_passed,
        )
