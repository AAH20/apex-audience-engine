"""Unit Tests for HyperFrames, Remotion, and Screenshots-to-GIF Cinema Subsystems."""

import json
import unittest

from apex_audience_engine.actuation.launch_dossier import LaunchDossierBuilder
from apex_audience_engine.actuation.pipeline import ApexAudiencePipeline, LaunchSpec
from apex_audience_engine.cinema.gif_pipeline import (
    GifCaptureRoute,
    GifPipelineOptions,
    PurePythonGifGenerator,
    ScreenshotsToGifPipeline,
)
from apex_audience_engine.cinema.hyperframes import (
    HyperFramesCompiler,
    HyperFramesOptions,
    HyperFramesTheme,
)
from apex_audience_engine.cinema.montage import OpenMontageCompiler
from apex_audience_engine.cinema.remotion import (
    RemotionProjectCompiler,
    RemotionProjectConfig,
)
from apex_audience_engine.mirofish.metrics import PreMortemReport


class TestCinemaExtended(unittest.TestCase):
    def setUp(self):
        self.timeline = OpenMontageCompiler.build_technical_launch_montage(
            project_name="Apex-Kernel",
            problem_statement="Combinatorial NP-hard complexity in global freight",
            primary_benchmark="p50=1.03ms (176k ops/s)",
            architecture_focus="Directed Acyclic Graph DAG coordination mesh",
            install_command="pip install apex-kernel",
        )

    def test_hyperframes_html_contract(self):
        """Verifies HyperFrames HTML satisfies the hyperframes-core contract."""
        compiler = HyperFramesCompiler(HyperFramesOptions(composition_id="ApexLaunchTrailer"))
        html = compiler.compile_html(self.timeline)

        self.assertIn("<!DOCTYPE html>", html)
        self.assertIn('data-composition-id="ApexLaunchTrailer"', html)
        self.assertIn('data-width="1920"', html)
        self.assertIn('data-height="1080"', html)
        self.assertIn('data-fps="30"', html)
        self.assertIn('window.__timelines["ApexLaunchTrailer"]', html)

        # Check clip attributes
        self.assertIn('class="clip"', html)
        self.assertIn('data-track-index="0"', html)
        self.assertIn('data-start="0.00"', html)

        # Check no forbidden translate conflict on root
        self.assertNotIn("transform: translate(-50%,-50%)", html)

    def test_hyperframes_project_json_and_ledger(self):
        """Verifies hyperframes.json project definition and media-use ledger."""
        compiler = HyperFramesCompiler()
        p_json = compiler.compile_project_json(self.timeline)
        self.assertEqual(p_json["version"], "1.0.0")
        self.assertEqual(p_json["canvas"]["width"], 1920)
        self.assertEqual(p_json["canvas"]["height"], 1080)
        self.assertEqual(len(p_json["tracks"][0]["clips"]), len(self.timeline.shots))
        self.assertIn("preview", p_json["cli_commands"])
        self.assertIn("render", p_json["cli_commands"])

        ledger = compiler.compile_media_ledger(self.timeline)
        self.assertIn("resolved_assets", ledger)
        self.assertIn("bgm", ledger["resolved_assets"])
        self.assertIn("sfx", ledger["resolved_assets"])
        self.assertIn("grade", ledger["resolved_assets"])

    def test_remotion_project_compilation(self):
        """Verifies Remotion project complies with remotion-markup & best practices."""
        compiler = RemotionProjectCompiler(RemotionProjectConfig(composition_id="ApexTrailer"))
        files = compiler.compile_project(self.timeline)

        expected_files = [
            "package.json",
            "remotion.config.ts",
            "tsconfig.json",
            "src/index.ts",
            "src/Root.tsx",
            "src/MainComposition.tsx",
            "src/components/SceneCard.tsx",
            "src/components/CaptionsTrack.tsx",
            "src/components/TelemetryHud.tsx",
            "src/types.ts",
            "README.md",
        ]
        for f in expected_files:
            self.assertIn(f, files, f"Missing expected Remotion file: {f}")

        # Check package.json dependencies
        pkg = json.loads(files["package.json"])
        self.assertIn("remotion", pkg["dependencies"])
        self.assertIn("@remotion/cli", pkg["dependencies"])
        self.assertIn("@remotion/captions", pkg["dependencies"])

        # Check Root.tsx composition declaration
        self.assertIn('<Composition', files["src/Root.tsx"])
        self.assertIn('id="ApexTrailer"', files["src/Root.tsx"])

        # Check MainComposition Series & AbsoluteFill
        self.assertIn('<Series>', files["src/MainComposition.tsx"])
        self.assertIn('<AbsoluteFill', files["src/MainComposition.tsx"])

    def test_screenshots_to_gif_pipeline_script(self):
        """Verifies bash script generation strictly implements screenshots-to-gif-demo."""
        pipeline = ScreenshotsToGifPipeline(GifPipelineOptions(
            base_url="http://localhost:8000",
            output_gif_path="out/demo.gif",
            routes=[
                GifCaptureRoute("home", "/home", 2.0),
                GifCaptureRoute("stats", "/stats", 2.0),
            ],
        ))
        script = pipeline.generate_shell_script()

        # Check Chrome headless parameters from skill
        self.assertIn("--headless", script)
        self.assertIn("--disable-gpu", script)
        self.assertIn("--no-sandbox", script)
        self.assertIn("--virtual-time-budget=5000", script)
        self.assertIn("--window-size=1920,1080", script)
        self.assertIn("--hide-scrollbars", script)
        self.assertIn("--run-all-compositor-stages-before-draw", script)

        # Check FFmpeg palettegen & dithering
        self.assertIn("palettegen=max_colors=128", script)
        self.assertIn("paletteuse=dither=bayer", script)
        self.assertIn("scale=1280:-1:flags=lanczos", script)
        self.assertIn("-loop 0", script)

        manifest = pipeline.generate_manifest_json()
        self.assertEqual(manifest["pipeline"], "screenshots-to-gif-demo")
        self.assertEqual(len(manifest["routes"]), 2)

    def test_pure_python_gif_generator(self):
        """Verifies pure Python fallback produces valid GIF89a binary header and trailer."""
        gif_bytes = PurePythonGifGenerator.create_minimal_animated_gif(width=64, height=36, frame_count=2)
        self.assertTrue(gif_bytes.startswith(b"GIF89a"), "Must start with GIF89a magic bytes")
        self.assertTrue(gif_bytes.endswith(b"\x3B"), "Must terminate with GIF trailer 0x3B")
        self.assertGreater(len(gif_bytes), 50)

    def test_launch_package_integration(self):
        """Verifies MasterLaunchPackage includes HyperFrames, Remotion, and GIF assets."""
        pre_mortem = PreMortemReport(
            total_personas_simulated=25,
            overall_receptivity_index=1.45,
            flame_war_probability=0.04,
            upvote_velocity_score=0.88,
            tribe_resonance={"Systems Engineers": 0.95},
            flagged_friction_points=[],
            prescriptive_recommendations=["Release benchmark logs"],
            simulation_passed=True,
        )
        package = LaunchDossierBuilder.build_package(
            project_name="Apex-Kernel",
            tagline="Ultra Fast Solver",
            cleaned_prose="Deterministic execution.",
            benchmark_table="| Benchmark | Latency |",
            architecture_summary="DAG multi-kernel",
            install_command="pip install apex-kernel",
            repo_url="https://github.com/AAH20/apex-kernel",
            timeline=self.timeline,
            pre_mortem=pre_mortem,
        )

        self.assertTrue(len(package.hyperframes_html) > 100)
        self.assertIn("ApexKernel", package.hyperframes_html)
        self.assertTrue(len(package.remotion_project_files) >= 10)
        self.assertIn("src/Root.tsx", package.remotion_project_files)
        self.assertTrue(len(package.screenshots_gif_script) > 100)
        self.assertIn("--virtual-time-budget=5000", package.screenshots_gif_script)


if __name__ == "__main__":
    unittest.main()
