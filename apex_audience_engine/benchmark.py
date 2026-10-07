"""Microsecond Benchmark Telemetry Suite for Apex Audience Engine.

Measures p50, p99, and ops/sec for all 10 core subsystems on pure Python standard library.
"""

from __future__ import annotations

import time
from typing import Any, Callable, Dict, List

from apex_audience_engine.actuation.pipeline import ApexAudiencePipeline, LaunchSpec
from apex_audience_engine.antislop.entropy import EntropyCalculator
from apex_audience_engine.antislop.heuristics import SlopHeuristicsEngine
from apex_audience_engine.antislop.linter import AntiSlopEngine
from apex_audience_engine.cinema.camera import CameraDirector, CameraMotionPreset
from apex_audience_engine.cinema.montage import OpenMontageCompiler
from apex_audience_engine.decisions.clef import CloudflareClefEngine
from apex_audience_engine.decisions.laya import LayaLocalRouter
from apex_audience_engine.mesh.np_hard_bridge import NPHardSwarmOptimizer, SwarmAllocationItem
from apex_audience_engine.mirofish.simulator import MiroFishSwarmSimulator


class BenchmarkHarness:
    """Benchmark suite calculating microsecond telemetry."""

    ITERATIONS = 100

    def __init__(self) -> None:
        self.antislop = AntiSlopEngine()
        self.heuristics = SlopHeuristicsEngine()
        self.entropy = EntropyCalculator()
        self.mirofish = MiroFishSwarmSimulator()
        self.clef = CloudflareClefEngine()
        self.laya = LayaLocalRouter()
        self.pipeline = ApexAudiencePipeline()

    def run_all(self) -> dict[str, dict[str, float]]:
        sample_ai_text = (
            "AI-assisted coding stands as a testament to the transformative power of modern tech. "
            "In today's rapidly evolving landscape, this groundbreaking tool features great UI, "
            "underscoring its pivotal role. Let's dive in! What makes an API good? It comes down to speed."
        )

        results: dict[str, dict[str, float]] = {}

        # 1. Slop Heuristics Linter
        results["1. Anti-Slop 34-Rule Linter"] = self._time_fn(
            lambda: self.heuristics.audit(sample_ai_text)
        )

        # 2. Shannon Entropy & PID Calculator
        results["2. Shannon Entropy & PID"] = self._time_fn(
            lambda: self.entropy.calculate(sample_ai_text, 4)
        )

        # 3. Full Anti-Slop Rewrite Pipeline
        results["3. Anti-Slop De-AI Transformation"] = self._time_fn(
            lambda: self.antislop.process(sample_ai_text)
        )

        # 4. Higgsfield 3D Camera Trajectory
        results["4. 3D Camera Trajectory Gen"] = self._time_fn(
            lambda: CameraDirector.generate_trajectory(CameraMotionPreset.ORBIT_360, 4.0)
        )

        # 5. Open Montage Timeline Compiler
        results["5. Open Montage Storyboard Compiler"] = self._time_fn(
            lambda: OpenMontageCompiler.build_technical_launch_montage(
                "Apex", "Problem", "100us", "Arch", "pip install"
            )
        )

        # 6. Cloudflare Clef System 1 Decision
        results["6. Cloudflare Clef Hot-Path Gate"] = self._time_fn(
            lambda: self.clef.evaluate_slop_gate(sample_ai_text, 3, 0.25)
        )

        # 7. Laya Local Comment Triage
        results["7. Laya Local Feedback Router"] = self._time_fn(
            lambda: self.laya.triage_comment("The benchmark ran in 12ms and reproduced perfectly on Linux!")
        )

        # 8. MiroFish 25-Persona Pre-Mortem Swarm
        results["8. MiroFish 25-Persona Swarm Sim"] = self._time_fn(
            lambda: self.mirofish.simulate_launch("Show HN: Fast Engine", "Pure python stdlib zero deps", "1ms", True)
        )

        # 9. NP-Hard MCKP Attention Budget
        tribe_options = {
            "sys": [SwarmAllocationItem("sys", "low", 10.0, 100), SwarmAllocationItem("sys", "deep", 25.0, 300)],
            "quant": [SwarmAllocationItem("quant", "low", 12.0, 100), SwarmAllocationItem("quant", "deep", 30.0, 350)],
            "indie": [SwarmAllocationItem("indie", "low", 8.0, 80), SwarmAllocationItem("indie", "deep", 20.0, 250)],
        }
        results["9. NP-Hard MCKP Budget Optimizer"] = self._time_fn(
            lambda: NPHardSwarmOptimizer.solve_mckp_attention_budget(tribe_options, 600)
        )

        # 10. End-to-End Master Launch Pipeline
        spec = LaunchSpec(
            project_name="Apex-Kernel",
            tagline="Deterministic Solver",
            draft_copy=sample_ai_text,
            problem_statement="Combinatorial explosion",
            benchmark_metrics="p50=42us",
            architecture_summary="Graph DAG",
            install_command="pip install apex-kernel",
            repo_url="https://github.com/AAH20/apex-kernel",
        )
        results["10. Master Pipeline End-to-End"] = self._time_fn(
            lambda: self.pipeline.run(spec)
        )

        return results

    def _time_fn(self, fn: Callable[[], Any]) -> dict[str, float]:
        # Warmup
        for _ in range(5):
            fn()

        latencies_us: list[float] = []
        for _ in range(self.ITERATIONS):
            t0 = time.perf_counter()
            fn()
            latencies_us.append((time.perf_counter() - t0) * 1_000_000.0)

        latencies_us.sort()
        p50 = latencies_us[int(len(latencies_us) * 0.50)]
        p99 = latencies_us[int(len(latencies_us) * 0.99)]
        ops_sec = int(1_000_000.0 / p50) if p50 > 0 else 0

        return {"p50_us": round(p50, 2), "p99_us": round(p99, 2), "ops_sec": ops_sec}

    def print_report(self) -> None:
        metrics = self.run_all()
        print("=" * 80)
        print("  Apex Audience Engine — Subsystem Benchmark Telemetry")
        print("=" * 80)
        print(f"  {'Audience & Launch Subsystem':<46} {'p50 (µs)':>10} {'p99 (µs)':>10} {'Ops/sec':>10}")
        print("  " + "-" * 46 + " " + "-" * 10 + " " + "-" * 10 + " " + "-" * 10)

        tot_p50 = sum(m["p50_us"] for m in metrics.values())
        for name, m in metrics.items():
            print(f"  {name:<46} {m['p50_us']:>10.2f} {m['p99_us']:>10.2f} {m['ops_sec']:>10}")

        print("  " + "-" * 46 + " " + "-" * 10 + " " + "-" * 10 + " " + "-" * 10)
        print(f"  PIPELINE AGGREGATE p50 LATENCY                  {tot_p50:>10.2f} µs ({tot_p50/1000.0:.2f} ms)")
        print("=" * 80)


if __name__ == "__main__":
    BenchmarkHarness().print_report()
