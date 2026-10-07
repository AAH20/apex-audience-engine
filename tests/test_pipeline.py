"""Tests for Master Pipeline Subsystem."""

import unittest

from apex_audience_engine.actuation.pipeline import ApexAudiencePipeline, LaunchSpec


class TestPipeline(unittest.TestCase):

    def test_full_pipeline_execution(self) -> None:
        spec = LaunchSpec(
            project_name="Apex-Kernel",
            tagline="Deterministic Solver",
            draft_copy="This serves as a testament to speed in today's evolving landscape. What makes an API good? Speed.",
            problem_statement="High latency in traditional solvers",
            benchmark_metrics="42 µs per query (23,000 ops/sec)",
            architecture_summary="Directed acyclic graph memory kernel",
            install_command="pip install apex-kernel",
            repo_url="https://github.com/AAH20/apex-kernel",
        )
        pipeline = ApexAudiencePipeline()
        res = pipeline.run(spec)

        self.assertIsNotNone(res.audit_result)
        self.assertIsNotNone(res.montage_timeline)
        self.assertIsNotNone(res.pre_mortem_report)
        self.assertIsNotNone(res.headline_selection)
        self.assertIsNotNone(res.launch_package)
        self.assertLess(res.pipeline_execution_time_ms, 50.0)  # Sub-50ms guarantee


if __name__ == "__main__":
    unittest.main()
