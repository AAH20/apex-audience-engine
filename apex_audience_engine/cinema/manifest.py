"""Video Compilation Manifest Exporter.

Translates MontageTimeline objects into execution-ready JSON manifests
for Remotion React rendering, VideoClaw CLI scripts, and HyperFrames cloud rendering.
"""

from __future__ import annotations

import json
from typing import Any, Dict

from apex_audience_engine.cinema.montage import MontageTimeline


class VideoManifestExporter:
    """Exports Montage timelines to rendering engine formats."""

    @staticmethod
    def to_remotion_manifest(timeline: MontageTimeline) -> dict[str, Any]:
        """Generates props dictionary for Remotion React compositions."""
        scenes = []
        for s in timeline.shots:
            scenes.append(
                {
                    "id": s.shot_id,
                    "type": s.shot_type.value,
                    "headline": s.headline,
                    "content": s.code_or_metric_payload,
                    "durationFrames": int(s.duration_sec * 30),  # 30 fps
                    "cameraPreset": s.camera_trajectory.preset.value,
                    "transition": s.transition_out.value,
                    "audioCue": s.foley_cue.value,
                }
            )

        return {
            "compositionId": "ApexTechnicalLaunchTrailer",
            "fps": 30,
            "width": 1920,
            "height": 1080,
            "totalDurationFrames": int(timeline.total_duration_sec * 30),
            "scenes": scenes,
        }

    @staticmethod
    def to_videoclaw_recipe(timeline: MontageTimeline) -> dict[str, Any]:
        """Generates VideoClaw CLI vclaw project definition."""
        steps = []
        for s in timeline.shots:
            steps.append(
                {
                    "action": "render_scene",
                    "template": s.shot_type.value,
                    "duration": s.duration_sec,
                    "params": {
                        "text": s.headline,
                        "code": s.code_or_metric_payload,
                        "camera": s.camera_trajectory.preset.value,
                    },
                }
            )

        return {
            "project_name": timeline.title.replace(" ", "_").lower(),
            "target_resolution": "1080p",
            "timeline": steps,
        }
