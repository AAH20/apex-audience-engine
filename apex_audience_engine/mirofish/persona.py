"""Epistemic Tribe Personas for MiroFish Synthetic Audience Simulation.

Models distinct developer and technical audiences with formal cognitive priors,
skepticism thresholds, and specific rejection/acceptance triggers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Set


class EpistemicTribe(str, Enum):
    SYSTEMS_ENGINEER = "systems_engineer"
    QUANT_RESEARCHER = "quant_researcher"
    INDIE_HACKER = "indie_hacker"
    VENTURE_ALLOCATOR = "venture_allocator"
    TECH_TWITTER_CRITIC = "tech_twitter_critic"


@dataclass
class SyntheticPersona:
    id: str
    tribe: EpistemicTribe
    name: str
    rejection_triggers: set[str] = field(default_factory=set)
    acceptance_drivers: set[str] = field(default_factory=set)
    base_skepticism: float = 0.5  # 0.0 (naive trust) to 1.0 (hardened cynic)
    influence_weight: float = 1.0


class PersonaFactory:
    """Builds calibrated synthetic personas across developer archetypes."""

    @staticmethod
    def create_default_swarm(size_per_tribe: int = 5) -> list[SyntheticPersona]:
        personas: list[SyntheticPersona] = []

        # 1. Systems Engineers
        for i in range(size_per_tribe):
            personas.append(
                SyntheticPersona(
                    id=f"sys_eng_{i+1}",
                    tribe=EpistemicTribe.SYSTEMS_ENGINEER,
                    name=f"Senior Systems Engineer {i+1}",
                    rejection_triggers={
                        "game-changer", "revolutionary", "seamless", "delve",
                        "no source code", "heavy docker required", "unverified benchmark"
                    },
                    acceptance_drivers={
                        "zero dependencies", "zero dependency", "pure python standard library",
                        "pure python", "standard library", "microsecond", "reproducible",
                        "c++", "rust", "linux", "ast", "clean stdlib"
                    },
                    base_skepticism=0.85,
                    influence_weight=1.5,
                )
            )

        # 2. Quant Researchers
        for i in range(size_per_tribe):
            personas.append(
                SyntheticPersona(
                    id=f"quant_{i+1}",
                    tribe=EpistemicTribe.QUANT_RESEARCHER,
                    name=f"Quant Researcher {i+1}",
                    rejection_triggers={
                        "miracle algorithm", "guaranteed profit", "unstoppable", "magic"
                    },
                    acceptance_drivers={
                        "np-hard", "deterministic", "worst-case bound", "admiralty",
                        "clarke-wright", "submodular", "mathematical formulation", "katex",
                        "benchmarks", "p50"
                    },
                    base_skepticism=0.90,
                    influence_weight=1.3,
                )
            )

        # 3. Indie Hackers
        for i in range(size_per_tribe):
            personas.append(
                SyntheticPersona(
                    id=f"indie_{i+1}",
                    tribe=EpistemicTribe.INDIE_HACKER,
                    name=f"Indie Builder {i+1}",
                    rejection_triggers={
                        "enterprise pricing only", "contact sales", "overengineered", "closed source"
                    },
                    acceptance_drivers={
                        "pip install", "quickstart", "fast setup", "open source",
                        "mit license", "apache-2.0", "self-hosted"
                    },
                    base_skepticism=0.45,
                    influence_weight=1.0,
                )
            )

        # 4. Venture Allocators
        for i in range(size_per_tribe):
            personas.append(
                SyntheticPersona(
                    id=f"vc_{i+1}",
                    tribe=EpistemicTribe.VENTURE_ALLOCATOR,
                    name=f"Technical Partner {i+1}",
                    rejection_triggers={
                        "toy project", "unmaintainable", "no moat", "wrapper script"
                    },
                    acceptance_drivers={
                        "sovereign platform", "infrastructure", "deep tech", "mcp", "tam"
                    },
                    base_skepticism=0.60,
                    influence_weight=1.2,
                )
            )

        # 5. Tech Twitter Critics
        for i in range(size_per_tribe):
            personas.append(
                SyntheticPersona(
                    id=f"critic_{i+1}",
                    tribe=EpistemicTribe.TECH_TWITTER_CRITIC,
                    name=f"Tech Commentator {i+1}",
                    rejection_triggers={
                        "delve", "testament", "tapestry", "in today's world",
                        "money printer", "passive income", "ai slop"
                    },
                    acceptance_drivers={
                        "anti-slop", "honest post mortem", "real benchmarks",
                        "unfiltered demonstration", "sharp criticism"
                    },
                    base_skepticism=0.95,
                    influence_weight=1.8,
                )
            )

        return personas
