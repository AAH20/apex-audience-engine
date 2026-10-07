"""CLI Interface for Apex Audience Engine."""

from __future__ import annotations

import argparse
import json
import sys

from apex_audience_engine.actuation.pipeline import ApexAudiencePipeline, LaunchSpec
from apex_audience_engine.antislop.linter import AntiSlopEngine
from apex_audience_engine.benchmark import BenchmarkHarness
from apex_audience_engine.cinema.manifest import VideoManifestExporter
from apex_audience_engine.cinema.montage import OpenMontageCompiler
from apex_audience_engine.decisions.laya import LayaLocalRouter
from apex_audience_engine.mirofish.simulator import MiroFishSwarmSimulator


def cmd_benchmark() -> None:
    BenchmarkHarness().print_report()


def cmd_audit(text: str) -> None:
    engine = AntiSlopEngine()
    res = engine.process(text)
    print("=" * 80)
    print("  Apex Audience Engine — Anti-Slop Audit Report")
    print("=" * 80)
    print(f"Original Words: {res.original_metrics.word_count} | Cleaned Words: {res.cleaned_metrics.word_count}")
    print(f"Slop Violations Found: {len(res.violations)}")
    for v in res.violations:
        print(f"  → [Rule {v.rule_id}: {v.rule_name}] '{v.matched_phrase}' => suggest '{v.suggested_replacement}'")
    print("-" * 80)
    print(f"Slop Index: {res.original_metrics.slop_index:.2f} -> {res.cleaned_metrics.slop_index:.2f} (-{res.slop_reduction_pct:.1f}%)")
    print(f"Propositional Density: {res.original_metrics.propositional_density:.2f} -> {res.cleaned_metrics.propositional_density:.2f}")
    print(f"Audit Passed: {res.audit_passed}")
    print("=" * 80)
    print("CLEANED TEXT:")
    print(res.cleaned_text)
    print("=" * 80)


def cmd_cinema(project: str, benchmark: str) -> None:
    timeline = OpenMontageCompiler.build_technical_launch_montage(
        project_name=project,
        problem_statement="Combinatorial complexity bottleneck",
        primary_benchmark=benchmark,
        architecture_focus="Directed Acyclic Graph multi-kernel pipeline",
        install_command=f"pip install {project.lower()}",
    )
    manifest = VideoManifestExporter.to_remotion_manifest(timeline)
    print("=" * 80)
    print(f"  Apex Audience Engine — Open Montage Storyboard: {project}")
    print("=" * 80)
    print(f"Total Duration: {timeline.total_duration_sec}s | Average Shot Length: {timeline.average_shot_length_sec}s")
    for s in timeline.shots:
        print(f"  Shot [{s.shot_id}] ({s.duration_sec}s): {s.headline}")
        print(f"    Camera: {s.camera_trajectory.preset.value} | Foley: {s.foley_cue.value} | Cut: {s.transition_out.value}")
    print("-" * 80)
    print("Remotion Composition Manifest (Preview):")
    print(json.dumps(manifest, indent=2)[:400] + "\n...")


def cmd_simulate(headline: str, body: str) -> None:
    sim = MiroFishSwarmSimulator()
    rep = sim.simulate_launch(headline, body, "sub-millisecond execution", True)
    print("=" * 80)
    print("  Apex Audience Engine — MiroFish Pre-Mortem Swarm Simulation")
    print("=" * 80)
    print(f"Personas Simulated: {rep.total_personas_simulated} across 5 Epistemic Tribes")
    print(f"Receptivity Index (RVI): {rep.overall_receptivity_index:.2f} (Target > 1.20)")
    print(f"Flame-War Probability: {rep.flame_war_probability*100:.1f}%")
    print(f"Simulation Status: {'PASSED (Front-Page Viable)' if rep.simulation_passed else 'FAILED (High Skepticism)'}")
    print("-" * 80)
    print("Tribal Resonance Breakdown:")
    for tribe, score in rep.tribe_resonance.items():
        print(f"  - {tribe:<22}: {score:.2f} / 1.00")
    if rep.flagged_friction_points:
        print("-" * 80)
        print("Flagged Friction Points:")
        for fp in rep.flagged_friction_points:
            print(f"  ! {fp}")
    print("-" * 80)
    print("Prescriptive Fixes:")
    for r in rep.prescriptive_recommendations:
        print(f"  ✓ {r}")
    print("=" * 80)


def cmd_triage(comment: str) -> None:
    router = LayaLocalRouter()
    dec = router.triage_comment(comment)
    print("=" * 80)
    print("  Apex Audience Engine — Laya System 1 Comment Triage")
    print("=" * 80)
    print(f"Comment: \"{dec.comment_text}\"")
    print(f"Action: {dec.action.value} (Confidence: {dec.confidence*100:.1f}%)")
    print(f"Reason: {dec.routing_reason}")
    print(f"Latency: {dec.latency_microseconds:.1f} µs")
    print("=" * 80)


def cmd_demo() -> None:
    sample_raw_draft = (
        "Apex-Autonomous-Logistics-Platform stands as a testament to the transformative power of "
        "AI agents in global shipping. In today's rapidly evolving logistics landscape, this groundbreaking "
        "platform boasts 8 incredible solvers, underscoring its pivotal role. Let's dive in! "
        "What makes supply chain optimization so hard? It comes down to NP-hard complexity."
    )
    spec = LaunchSpec(
        project_name="Apex-Autonomous-Logistics-Platform",
        tagline="Deterministic Zero-Dependency Global Freight Operating System",
        draft_copy=sample_raw_draft,
        problem_statement="Global shipping choke-points and container axle overloads cause multi-billion dollar losses.",
        benchmark_metrics="Pipeline p50 aggregate: 1.03 ms across all 8 solvers (176,460 ops/sec).",
        architecture_summary="Unified 6-tier architecture: Ingress, Maritime Zermelo, Intermodal 3D MES, Multi-Echelon GSM, Drone-Van FSTSP, Actuation.",
        install_command="git clone https://github.com/AAH20/apex-autonomous-logistics-platform.git",
        repo_url="https://github.com/AAH20/apex-autonomous-logistics-platform",
    )
    pipeline = ApexAudiencePipeline()
    res = pipeline.run(spec)

    print("=" * 80)
    print("  Apex Audience Engine — End-to-End Launch Demonstration")
    print("=" * 80)
    print(f"Pipeline Latency: {res.pipeline_execution_time_ms:.2f} ms")
    print(f"Slop Reduction: -{res.audit_result.slop_reduction_pct:.1f}% | New Slop Index: {res.audit_result.cleaned_metrics.slop_index:.2f}")
    print(f"Selected Channel: {res.headline_selection.target_channel.value} (Confidence: {res.headline_selection.clef_decision.confidence*100:.1f}%)")
    print(f"MiroFish RVI: {res.pre_mortem_report.overall_receptivity_index:.2f} | Flame Risk: {res.pre_mortem_report.flame_war_probability*100:.1f}%")
    print("-" * 80)
    print("SHOW HN DRAFT PREVIEW:")
    print(res.launch_package.show_hn.title)
    print("-" * 40)
    print(res.launch_package.show_hn.body_markdown[:350] + "\n...")
    print("=" * 80)


def main() -> None:
    parser = argparse.ArgumentParser(description="Apex Audience Engine CLI")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("benchmark", help="Run microsecond benchmark suite")
    subparsers.add_parser("demo", help="Run full end-to-end launch demo")

    audit_parser = subparsers.add_parser("audit", help="Audit text for AI slop")
    audit_parser.add_argument("text", type=str, help="Text to audit")

    cinema_parser = subparsers.add_parser("cinema", help="Generate cinematic montage")
    cinema_parser.add_argument("project", type=str, help="Project name")
    cinema_parser.add_argument("benchmark", type=str, help="Primary benchmark")

    sim_parser = subparsers.add_parser("simulate", help="Run MiroFish pre-mortem")
    sim_parser.add_argument("headline", type=str, help="Launch headline")
    sim_parser.add_argument("body", type=str, help="Launch body")

    triage_parser = subparsers.add_parser("triage", help="Triage community feedback")
    triage_parser.add_argument("comment", type=str, help="Comment to triage")

    args = parser.parse_args()

    if args.command == "benchmark":
        cmd_benchmark()
    elif args.command == "demo":
        cmd_demo()
    elif args.command == "audit":
        cmd_audit(args.text)
    elif args.command == "cinema":
        cmd_cinema(args.project, args.benchmark)
    elif args.command == "simulate":
        cmd_simulate(args.headline, args.body)
    elif args.command == "triage":
        cmd_triage(args.comment)
    else:
        cmd_demo()


if __name__ == "__main__":
    main()
