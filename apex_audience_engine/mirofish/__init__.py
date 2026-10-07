"""MiroFish Synthetic Audience Subsystem."""

from apex_audience_engine.mirofish.metrics import PersonaReaction, PreMortemReport
from apex_audience_engine.mirofish.persona import (
    EpistemicTribe,
    PersonaFactory,
    SyntheticPersona,
)
from apex_audience_engine.mirofish.simulator import MiroFishSwarmSimulator

__all__ = [
    "EpistemicTribe",
    "SyntheticPersona",
    "PersonaFactory",
    "PersonaReaction",
    "PreMortemReport",
    "MiroFishSwarmSimulator",
]
