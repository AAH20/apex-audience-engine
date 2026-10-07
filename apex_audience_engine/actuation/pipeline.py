"""Master Pipeline — Orchestrates the End-to-End Audience Engineering Lifecycle."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import List, Optional

from apex_audience_engine.actuation.launch_dossier import LaunchDossierBuilder, MasterLaunchPackage
from apex_audience_engine.antislop.linter import AntiSlopAuditResult, AntiSlopEngine
from apex_audience_engine.cinema.montage import MontageTimeline, OpenMontageCompiler
from apex_audience_engine.decisions.router import DecisionHotPathRouter, HeadlineSelectionResult
from apex_audience_engine.mirofish.metrics import PreMortemReport
from apex_audience_engine.mirofish.simulator import MiroFishSwarmSimulator


@dataclass
class LaunchSpec:
    project_name: str
    tagline: str
    draft_copy: str
    problem_statement: str
    benchmark_metrics: str
    architecture_summary: str
    install_command: str
    repo_url: str
    voice_sample: Optional[str] = None
    candidate_headlines: list[str] = field(default_factory=list)


@dataclass
class LaunchPipelineResult:
    spec: LaunchSpec
    audit_result: AntiSlopAuditResult
    montage_timeline: MontageTimeline
    pre_mortem_report: PreMortemReport
    headline_selection: HeadlineSelectionResult
    launch_package: MasterLaunchPackage
    pipeline_execution_time_ms: float


class ApexAudiencePipeline:
    """Master orchestrator executing the sovereign launch engineering workflow."""

    def __init__(self) -> None:
        self.antislop = AntiSlopEngine()
        self.mirofish = MiroFishSwarmSimulator()
        self.router = DecisionHotPathRouter()

    def run(self, spec: LaunchSpec) -> LaunchPipelineResult:
        t_start = time.perf_counter()

        # 1. Anti-Slop Audit & Transformation Pass
        audit_res = self.antislop.process(
            text=spec.draft_copy,
            voice_sample=spec.voice_sample,
            tradeoff_note="Pure Python standard library with microsecond execution.",
        )

        # 2. Cinematic Storyboard Compilation (Higgsfield + Open Montage)
        timeline = OpenMontageCompiler.build_technical_launch_montage(
            project_name=spec.project_name,
            problem_statement=spec.problem_statement,
            primary_benchmark=spec.benchmark_metrics,
            architecture_focus=spec.architecture_summary,
            install_command=spec.install_command,
        )

        # 3. Cloudflare Clef / Laya Rapid Decision Routing
        headlines = spec.candidate_headlines or [
            f"Show HN: {spec.project_name} – {spec.tagline}",
            f"{spec.project_name}: {spec.tagline} in pure Python",
            f"How we built {spec.project_name} with zero dependencies",
        ]
        headline_res = self.router.select_optimal_headline(headlines, audit_res.cleaned_text)

        # 4. MiroFish Synthetic Audience Pre-Mortem Simulation
        pre_mortem_res = self.mirofish.simulate_launch(
            headline=headline_res.best_headline,
            body_text=audit_res.cleaned_text,
            benchmark_claim=spec.benchmark_metrics,
            has_reproducible_code=True,
        )

        # 5. Master Launch Package Synthesis
        package = LaunchDossierBuilder.build_package(
            project_name=spec.project_name,
            tagline=spec.tagline,
            cleaned_prose=audit_res.cleaned_text,
            benchmark_table=spec.benchmark_metrics,
            architecture_summary=spec.architecture_summary,
            install_command=spec.install_command,
            repo_url=spec.repo_url,
            timeline=timeline,
            pre_mortem=pre_mortem_res,
        )

        t_elapsed_ms = (time.perf_counter() - t_start) * 1000.0

        return LaunchPipelineResult(
            spec=spec,
            audit_result=audit_res,
            montage_timeline=timeline,
            pre_mortem_report=pre_mortem_res,
            headline_selection=headline_res,
            launch_package=package,
            pipeline_execution_time_ms=round(t_elapsed_ms, 3),
        )
