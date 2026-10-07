"""HyperFrames HTML Video Composition Compiler.

Implements the official HyperFrames composition contract, based on Hermes skills:
- hyperframes (master router and workflow dispatcher)
- hyperframes-core (HTML data-* timing attributes, class="clip", tracks, determinism rules)
- hyperframes-animation (GSAP timelines, spring physics, staggered text, easing curves)
- hyperframes-creative (cinematic color tokens, video-medium depth, editorial typography)
- hyperframes-audio & media-use (Foley sound cues, audio track ledgers, BGM sync)
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from apex_audience_engine.cinema.montage import MontageShot, MontageTimeline, ShotType


@dataclass
class HyperFramesTheme:
    """Editorial styling tokens inspired by hyperframes-creative and Cathryn Lavery."""
    name: str = "editorial-dark"
    background: str = "#090d16"
    surface: str = "#131b2e"
    accent_focal: str = "#eb6c36"
    accent_telemetry: str = "#38bdf8"
    accent_store: str = "#818cf8"
    accent_success: str = "#10b981"
    text_primary: str = "#f8fafc"
    text_muted: str = "#94a3b8"
    font_family: str = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'SF Pro Display', sans-serif"
    font_mono: str = "'JetBrains Mono', 'SF Mono', Menlo, Consolas, monospace"


@dataclass
class HyperFramesOptions:
    """Configuration options for HyperFrames composition generation."""
    composition_id: str = "ApexTechnicalLaunchTrailer"
    width: int = 1920
    height: int = 1080
    fps: int = 30
    theme: HyperFramesTheme = field(default_factory=HyperFramesTheme)
    include_grid_backdrop: bool = True
    include_audio_markers: bool = True


class HyperFramesCompiler:
    """Compiles MontageTimelines into deterministic HyperFrames HTML compositions."""

    def __init__(self, options: Optional[HyperFramesOptions] = None) -> None:
        self.options = options or HyperFramesOptions()

    def compile_html(self, timeline: MontageTimeline) -> str:
        """Generates a complete, standalone HyperFrames HTML composition."""
        opts = self.options
        theme = opts.theme
        total_duration = timeline.total_duration_sec

        # Build clip HTML elements
        clips_html = []
        gsap_tweens = []

        cumulative_time = 0.0
        for idx, shot in enumerate(timeline.shots):
            start_time = cumulative_time
            end_time = cumulative_time + shot.duration_sec
            clip_id = f"clip-{idx:02d}-{shot.shot_id}"

            # Format visual payload based on shot type
            content_markup = self._format_shot_content(shot, theme)

            # HyperFrames core contract:
            # - class="clip"
            # - data-track-index="0"
            # - data-start="<seconds>"
            # - data-end="<seconds>"
            clip_elem = f"""      <!-- Shot {idx+1}: {shot.headline} ({shot.shot_type.value}) -->
      <div id="{clip_id}" class="clip" data-track-index="0" data-start="{start_time:.2f}" data-end="{end_time:.2f}">
        <div class="clip-container" id="container-{clip_id}">
          <div class="badge-tag">{shot.shot_type.value.upper()} · SCENE {idx+1:02d}</div>
          <h2 class="shot-headline" id="title-{clip_id}">{shot.headline}</h2>
          {content_markup}
          <div class="telemetry-bar">
            <span class="foley-pill">SFX: {shot.foley_cue.value}</span>
            <span class="camera-pill">CAM: {shot.camera_trajectory.preset.value}</span>
            <span class="timing-pill">{start_time:.1f}s – {end_time:.1f}s ({shot.duration_sec:.1f}s)</span>
          </div>
        </div>
      </div>"""
            clips_html.append(clip_elem)

            # GSAP animation timeline cues adhering to hyperframes-animation
            gsap_tweens.append(self._generate_gsap_cue(clip_id, start_time, shot.duration_sec))

            cumulative_time = end_time

        clips_body = "\n\n".join(clips_html)
        gsap_script = "\n".join(gsap_tweens)

        html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{timeline.title} — HyperFrames Composition</title>
  <!-- HyperFrames runtime dependency: GSAP 3.12+ for seekable timeline -->
  <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
  <style>
    /* =========================================================================
       HYPERFRAMES CORE SIZING & CANVAS CONTRACT
       ========================================================================= */
    *, *::before, *::after {{
      box-sizing: border-box;
    }}
    html, body {{
      margin: 0;
      padding: 0;
      width: 100%;
      height: 100%;
      overflow: hidden;
      background: {theme.background};
      color: {theme.text_primary};
      font-family: {theme.font_family};
      -webkit-font-smoothing: antialiased;
    }}
    #root {{
      width: 100%;
      height: 100%;
      position: relative;
      overflow: hidden;
      background: radial-gradient(circle at 50% 30%, {theme.surface} 0%, {theme.background} 80%);
    }}
    {self._get_grid_css(theme) if opts.include_grid_backdrop else ""}
    /* HyperFrames class="clip" positioning contract */
    .clip {{
      position: absolute;
      inset: 0;
      width: 100%;
      height: 100%;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 60px 100px;
      visibility: hidden; /* Managed by HyperFrames runtime engine */
      opacity: 0;
    }}
    .clip-container {{
      width: 100%;
      max-width: 1500px;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      text-align: center;
      position: relative;
      z-index: 10;
    }}
    .badge-tag {{
      display: inline-block;
      padding: 6px 16px;
      border-radius: 9999px;
      background: rgba(235, 108, 54, 0.15);
      border: 1px solid rgba(235, 108, 54, 0.4);
      color: {theme.accent_focal};
      font-family: {theme.font_mono};
      font-size: 13px;
      font-weight: 700;
      letter-spacing: 0.1em;
      margin-bottom: 24px;
      text-transform: uppercase;
    }}
    .shot-headline {{
      font-size: 56px;
      font-weight: 800;
      line-height: 1.15;
      margin: 0 0 32px 0;
      letter-spacing: -0.02em;
      max-width: 1200px;
      background: linear-gradient(180deg, #ffffff 0%, {theme.text_muted} 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }}
    .metric-hero {{
      display: flex;
      align-items: baseline;
      justify-content: center;
      gap: 12px;
      margin: 20px 0;
    }}
    .metric-value {{
      font-size: 96px;
      font-weight: 900;
      font-family: {theme.font_mono};
      color: {theme.accent_telemetry};
      text-shadow: 0 0 40px rgba(56, 189, 248, 0.35);
      letter-spacing: -0.04em;
    }}
    .metric-label {{
      font-size: 24px;
      color: {theme.text_muted};
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }}
    .code-terminal {{
      width: 100%;
      max-width: 1000px;
      background: #0d121f;
      border: 1px solid #1e293b;
      border-radius: 12px;
      padding: 24px 32px;
      text-align: left;
      font-family: {theme.font_mono};
      font-size: 20px;
      line-height: 1.5;
      color: #38bdf8;
      box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
      margin: 16px 0;
    }}
    .code-prompt {{
      color: {theme.accent_focal};
      margin-right: 12px;
      user-select: none;
    }}
    .telemetry-bar {{
      display: flex;
      gap: 16px;
      margin-top: 40px;
    }}
    .telemetry-bar span {{
      font-family: {theme.font_mono};
      font-size: 13px;
      padding: 6px 14px;
      border-radius: 6px;
      background: rgba(255, 255, 255, 0.04);
      border: 1px solid rgba(255, 255, 255, 0.08);
      color: {theme.text_muted};
    }}
    .foley-pill {{
      border-color: rgba(129, 140, 248, 0.3) !important;
      color: #c7d2fe !important;
    }}
    .camera-pill {{
      border-color: rgba(56, 189, 248, 0.3) !important;
      color: #bae6fd !important;
    }}
    .timing-pill {{
      border-color: rgba(16, 185, 129, 0.3) !important;
      color: #a7f3d0 !important;
    }}
  </style>
</head>
<body>
  <!-- HyperFrames Standalone Root Contract (data-* timing parameters) -->
  <div id="root"
       data-composition-id="{opts.composition_id}"
       data-width="{opts.width}"
       data-height="{opts.height}"
       data-duration="{total_duration:.2f}"
       data-fps="{opts.fps}">

{clips_body}

  </div>

  <!-- HyperFrames Seekable Animation Timeline Contract -->
  <script>
    (function() {{
      window.__timelines = window.__timelines || {{}};

      // Register exactly one paused GSAP timeline at window.__timelines[composition_id]
      const tl = gsap.timeline({{ paused: true }});
      window.__timelines["{opts.composition_id}"] = tl;

      // Master animated keyframes per shot
{gsap_script}

      console.log("[HyperFrames] Timeline initialized for {opts.composition_id} ({total_duration:.2f}s total)");
    }})();
  </script>
</body>
</html>
"""
        return html_template

    def compile_project_json(self, timeline: MontageTimeline) -> dict[str, Any]:
        """Generates hyperframes.json project definition for the HyperFrames CLI."""
        opts = self.options
        return {
            "version": "1.0.0",
            "project_name": opts.composition_id,
            "title": timeline.title,
            "main_composition": "index.html",
            "canvas": {
                "width": opts.width,
                "height": opts.height,
                "fps": opts.fps,
                "duration_sec": timeline.total_duration_sec,
            },
            "tracks": [
                {
                    "index": 0,
                    "type": "video",
                    "clips": [
                        {
                            "id": s.shot_id,
                            "type": s.shot_type.value,
                            "headline": s.headline,
                            "duration_sec": s.duration_sec,
                            "camera": s.camera_trajectory.preset.value,
                            "foley_cue": s.foley_cue.value,
                        }
                        for s in timeline.shots
                    ],
                }
            ],
            "audio": {
                "sample_rate": 48000,
                "bgm_track": {
                    "asset_id": "apex_launch_synthwave_bed",
                    "volume": 0.35,
                    "fade_in_sec": 1.0,
                    "fade_out_sec": 2.0,
                },
                "foley_cues": [
                    {
                        "shot_id": s.shot_id,
                        "cue": s.foley_cue.value,
                        "time_sec": sum(x.duration_sec for x in timeline.shots[:i]),
                    }
                    for i, s in enumerate(timeline.shots)
                ],
            },
            "cli_commands": {
                "preview": f"npx hyperframes preview index.html --port 3300",
                "render": f"npx hyperframes render index.html --output dist/{opts.composition_id}.mp4 --quality high",
                "timeline": "npx hyperframes timeline --json",
                "check": "npx hyperframes check",
            },
        }

    def compile_media_ledger(self, timeline: MontageTimeline) -> dict[str, Any]:
        """Generates an Agent Media OS (media-use) resolution ledger for bundled media assets."""
        return {
            "media_os_version": "2.0.0",
            "resolved_assets": {
                "bgm": {
                    "id": "apex-quantum-drive",
                    "type": "bgm",
                    "intent": "driving cyberpunk synthesizer bed for technical product launch",
                    "path": "assets/audio/bgm_quantum_drive.mp3",
                    "source": "heygen_catalog",
                },
                "sfx": [
                    {
                        "cue": s.foley_cue.value,
                        "resolved_file": f"assets/sfx/{s.foley_cue.value}.wav",
                        "timing_sec": sum(x.duration_sec for x in timeline.shots[:i]),
                    }
                    for i, s in enumerate(timeline.shots)
                ],
                "grade": {
                    "preset": "editorial-cold-matrix",
                    "lut": "assets/lut/matrix_clean_contrast.cube",
                    "intent": "high-contrast deep blacks with cyan-teal highlights",
                },
            },
        }

    def _format_shot_content(self, shot: MontageShot, theme: HyperFramesTheme) -> str:
        """Formats the visual payload inside the shot clip."""
        if shot.shot_type == ShotType.BENCHMARK_GRAPH:
            parts = shot.code_or_metric_payload.split("=")
            val = parts[1] if len(parts) > 1 else shot.code_or_metric_payload
            return f"""          <div class="metric-hero">
            <span class="metric-value">{val}</span>
            <span class="metric-label">{parts[0]}</span>
          </div>"""
        elif shot.shot_type in (ShotType.TERMINAL_EXECUTION, ShotType.CODE_SNIPPET):
            return f"""          <div class="code-terminal">
            <span class="code-prompt">&gt;</span>{shot.code_or_metric_payload}
          </div>"""
        else:
            return f"""          <p style="font-size: 26px; color: {theme.text_muted}; max-width: 900px; margin: 12px 0;">
            {shot.code_or_metric_payload}
          </p>"""

    def _generate_gsap_cue(self, clip_id: str, start_time: float, duration: float) -> str:
        """Generates seekable GSAP keyframe tweens adhering to hyperframes-core determinism."""
        in_time = f"{start_time:.2f}"
        out_time = f"{start_time + duration - 0.25:.2f}"

        return f"""      // Cue: #{clip_id}
      tl.set("#{clip_id}", {{ visibility: "visible", opacity: 0 }}, {in_time});
      tl.fromTo("#{clip_id}", 
        {{ opacity: 0, scale: 0.96 }}, 
        {{ opacity: 1, scale: 1.0, duration: 0.40, ease: "power2.out" }}, 
        {in_time}
      );
      tl.fromTo("#title-{clip_id}",
        {{ y: 30, opacity: 0 }},
        {{ y: 0, opacity: 1, duration: 0.45, ease: "back.out(1.2)" }},
        {float(in_time) + 0.10:.2f}
      );
      tl.to("#{clip_id}", 
        {{ opacity: 0, scale: 1.02, duration: 0.25, ease: "power1.in" }}, 
        {out_time}
      );
      tl.set("#{clip_id}", {{ visibility: "hidden" }}, {start_time + duration:.2f});"""

    def _get_grid_css(self, theme: HyperFramesTheme) -> str:
        return f"""    #root::before {{
      content: "";
      position: absolute;
      inset: 0;
      background-image: 
        linear-gradient(to right, rgba(255, 255, 255, 0.03) 1px, transparent 1px),
        linear-gradient(to bottom, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
      background-size: 80px 80px;
      pointer-events: none;
      z-index: 1;
    }}"""
