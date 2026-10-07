"""Open Montage Cut-on-Action Scene Graph & Timeline Compiler.

Compiles high-retention technical storyboards with cut-on-action transitions,
rhythmic shot lengths, and physical Foley sound design cues.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

from apex_audience_engine.cinema.camera import CameraDirector, CameraMotionPreset, CameraTrajectory


class ShotType(str, Enum):
    TERMINAL_EXECUTION = "terminal_execution"
    CODE_SNIPPET = "code_snippet"
    ARCHITECTURE_DIAGRAM = "architecture_diagram"
    BENCHMARK_GRAPH = "benchmark_graph"
    FOUNDER_GROUNDING = "founder_grounding"
    CALL_TO_ACTION = "call_to_action"


class CutTransition(str, Enum):
    HARD_CUT = "hard_cut"
    MATCH_CUT = "match_cut"
    WHIP_PAN = "whip_pan"
    RACK_TRANSITION = "rack_transition"


class FoleyCue(str, Enum):
    MECHANICAL_KEYSTROKE = "foley_mechanical_keystroke"
    SUB_BASS_DROP = "foley_sub_bass_drop"
    PENCIL_ON_PAPER = "foley_pencil_on_paper"
    METALLIC_SNAP = "foley_metallic_snap"
    SILENT_PAUSE = "foley_silent_pause"


@dataclass
class MontageShot:
    shot_id: str
    shot_type: ShotType
    headline: str
    code_or_metric_payload: str
    duration_sec: float
    camera_trajectory: CameraTrajectory
    transition_out: CutTransition = CutTransition.HARD_CUT
    foley_cue: FoleyCue = FoleyCue.MECHANICAL_KEYSTROKE


@dataclass
class MontageTimeline:
    title: str
    shots: list[MontageShot] = field(default_factory=list)
    total_duration_sec: float = 0.0
    average_shot_length_sec: float = 0.0

    def compile(self) -> None:
        """Calculates total duration and ASL."""
        self.total_duration_sec = sum(s.duration_sec for s in self.shots)
        self.average_shot_length_sec = (
            round(self.total_duration_sec / len(self.shots), 2) if self.shots else 0.0
        )


class OpenMontageCompiler:
    """Compiles programmatic technical launch trailers from raw product facts."""

    @staticmethod
    def build_technical_launch_montage(
        project_name: str,
        problem_statement: str,
        primary_benchmark: str,
        architecture_focus: str,
        install_command: str,
    ) -> MontageTimeline:
        """Builds a high-impact 15-second launch storyboard with zero fluff."""
        shots: list[MontageShot] = [
            # 1. Cold Hook: The Problem / Bottleneck (2.5s)
            MontageShot(
                shot_id="shot_01_hook",
                shot_type=ShotType.TERMINAL_EXECUTION,
                headline="The Bottleneck",
                code_or_metric_payload=problem_statement,
                duration_sec=2.5,
                camera_trajectory=CameraDirector.generate_trajectory(CameraMotionPreset.WHIP_PAN, 2.5),
                transition_out=CutTransition.HARD_CUT,
                foley_cue=FoleyCue.SUB_BASS_DROP,
            ),
            # 2. Hard Proof: Sub-Millisecond Benchmark (3.5s)
            MontageShot(
                shot_id="shot_02_proof",
                shot_type=ShotType.BENCHMARK_GRAPH,
                headline="Deterministic Benchmark",
                code_or_metric_payload=primary_benchmark,
                duration_sec=3.5,
                camera_trajectory=CameraDirector.generate_trajectory(CameraMotionPreset.SLOW_DOLLY_PUSH_IN, 3.5),
                transition_out=CutTransition.MATCH_CUT,
                foley_cue=FoleyCue.MECHANICAL_KEYSTROKE,
            ),
            # 3. Macro Architecture: The Mechanics (4.5s)
            MontageShot(
                shot_id="shot_03_architecture",
                shot_type=ShotType.ARCHITECTURE_DIAGRAM,
                headline="System Architecture",
                code_or_metric_payload=architecture_focus,
                duration_sec=4.5,
                camera_trajectory=CameraDirector.generate_trajectory(CameraMotionPreset.ORBIT_360, 4.5),
                transition_out=CutTransition.RACK_TRANSITION,
                foley_cue=FoleyCue.PENCIL_ON_PAPER,
            ),
            # 4. Immediate Reproducibility & Install (4.5s)
            MontageShot(
                shot_id="shot_04_install",
                shot_type=ShotType.CODE_SNIPPET,
                headline="Zero Dependencies",
                code_or_metric_payload=install_command,
                duration_sec=4.5,
                camera_trajectory=CameraDirector.generate_trajectory(CameraMotionPreset.STATIC_METRIC_HOLD, 4.5),
                transition_out=CutTransition.HARD_CUT,
                foley_cue=FoleyCue.METALLIC_SNAP,
            ),
        ]

        timeline = MontageTimeline(title=f"{project_name} Technical Launch", shots=shots)
        timeline.compile()
        return timeline
