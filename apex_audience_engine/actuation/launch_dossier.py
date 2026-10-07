"""Launch Dossier Builder — Synthesizes Publication-Grade Launch Packages."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from apex_audience_engine.cinema.gif_pipeline import (
    GifPipelineOptions,
    ScreenshotsToGifPipeline,
)
from apex_audience_engine.cinema.hyperframes import (
    HyperFramesCompiler,
    HyperFramesOptions,
)
from apex_audience_engine.cinema.montage import MontageTimeline
from apex_audience_engine.cinema.remotion import (
    RemotionProjectCompiler,
    RemotionProjectConfig,
)
from apex_audience_engine.mirofish.metrics import PreMortemReport


@dataclass
class ShowHNDossier:
    title: str
    body_markdown: str


@dataclass
class XTwitterThread:
    tweets: list[str]
    video_cues: list[str]


@dataclass
class RedditPost:
    subreddit: str
    title: str
    body_markdown: str


@dataclass
class MasterLaunchPackage:
    project_name: str
    show_hn: ShowHNDossier
    x_thread: XTwitterThread
    reddit_post: RedditPost
    montage_timeline: MontageTimeline
    pre_mortem_report: PreMortemReport
    hyperframes_html: str = ""
    hyperframes_project_json: dict[str, Any] = field(default_factory=dict)
    remotion_project_files: dict[str, str] = field(default_factory=dict)
    screenshots_gif_script: str = ""
    screenshots_gif_manifest: dict[str, Any] = field(default_factory=dict)


class LaunchDossierBuilder:
    """Builds complete, de-slopped, benchmark-dense launch packages."""

    @staticmethod
    def build_package(
        project_name: str,
        tagline: str,
        cleaned_prose: str,
        benchmark_table: str,
        architecture_summary: str,
        install_command: str,
        repo_url: str,
        timeline: MontageTimeline,
        pre_mortem: PreMortemReport,
    ) -> MasterLaunchPackage:
        # 1. Show HN Dossier (Humble, highly factual, zero marketing fluff)
        hn_title = f"Show HN: {project_name} – {tagline}"
        hn_body = f"""{cleaned_prose}

### Benchmark Telemetry
{benchmark_table}

### Architecture & Mechanics
{architecture_summary}

### Quickstart & Reproduction
```bash
{install_command}
```

Repository: {repo_url}

Feedback, criticism, and edge-case bug reports are warmly welcome."""

        # 2. X/Twitter Cinematic Thread
        tweets = [
            f"1/5 Introducing {project_name}: {tagline}.\n\nBuilt entirely for sub-millisecond execution with zero external dependencies.\n\n[Attached: 15s Cinematic Teaser]",
            f"2/5 Why we built it:\n\n{cleaned_prose[:240]}...",
            f"3/5 Benchmark Breakdown:\n\n{benchmark_table[:250]}\n\nZero Docker required. Runs directly in standard Python stdlib.",
            f"4/5 Architecture:\n\n{architecture_summary[:240]}...",
            f"5/5 Open source under Apache-2.0:\n\nRepo: {repo_url}\n\nInstall:\n{install_command}",
        ]
        video_cues = [f"Shot {s.shot_id}: {s.headline} ({s.camera_trajectory.preset.value})" for s in timeline.shots]

        # 3. Reddit Post
        reddit_title = f"I built {project_name} ({tagline}) – pure Python standard library, zero dependencies"
        reddit_body = f"""Hey everyone,

{cleaned_prose}

### Performance
{benchmark_table}

### Architecture
{architecture_summary}

Code and tests: {repo_url}
Install: `{install_command}`

Would love feedback on the implementation!"""

        # 4. HyperFrames HTML & Project Compilation (Hermes hyperframes skills)
        hf_opts = HyperFramesOptions(composition_id=project_name.replace("-", "_").title().replace("_", ""))
        hf_compiler = HyperFramesCompiler(hf_opts)
        hf_html = hf_compiler.compile_html(timeline)
        hf_json = hf_compiler.compile_project_json(timeline)

        # 5. Remotion React Project Compilation (Hermes remotion skills)
        remotion_cfg = RemotionProjectConfig(composition_id=project_name.replace("-", "_").title().replace("_", ""))
        remotion_compiler = RemotionProjectCompiler(remotion_cfg)
        remotion_files = remotion_compiler.compile_project(timeline)

        # 6. Screenshots to Animated GIF Automation (Hermes screenshots-to-gif-demo skill)
        gif_pipeline = ScreenshotsToGifPipeline(GifPipelineOptions(
            output_gif_path=f"dist/{project_name.lower().replace('-', '_')}_demo.gif",
            screenshots_dir=f"dist/screenshots_{project_name.lower().replace('-', '_')}",
        ))
        gif_script = gif_pipeline.generate_shell_script()
        gif_manifest = gif_pipeline.generate_manifest_json()

        return MasterLaunchPackage(
            project_name=project_name,
            show_hn=ShowHNDossier(title=hn_title, body_markdown=hn_body),
            x_thread=XTwitterThread(tweets=tweets, video_cues=video_cues),
            reddit_post=RedditPost(subreddit="r/Python", title=reddit_title, body_markdown=reddit_body),
            montage_timeline=timeline,
            pre_mortem_report=pre_mortem,
            hyperframes_html=hf_html,
            hyperframes_project_json=hf_json,
            remotion_project_files=remotion_files,
            screenshots_gif_script=gif_script,
            screenshots_gif_manifest=gif_manifest,
        )
