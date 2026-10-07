"""Tests for Cinema Subsystem."""

import unittest

from apex_audience_engine.cinema.camera import CameraDirector, CameraMotionPreset
from apex_audience_engine.cinema.manifest import VideoManifestExporter
from apex_audience_engine.cinema.montage import OpenMontageCompiler, ShotType


class TestCinema(unittest.TestCase):

    def test_camera_trajectory_interpolation(self) -> None:
        traj = CameraDirector.generate_trajectory(CameraMotionPreset.SLOW_DOLLY_PUSH_IN, duration_sec=4.0)
        self.assertEqual(len(traj.keyframes), 2)
        mid_kf = traj.interpolate(2.0)
        self.assertAlmostEqual(mid_kf.z, 1.6, places=2)
        self.assertEqual(mid_kf.timestamp_sec, 2.0)

    def test_orbit_trajectory_generation(self) -> None:
        traj = CameraDirector.generate_trajectory(CameraMotionPreset.ORBIT_360, duration_sec=4.0)
        self.assertEqual(len(traj.keyframes), 5)
        self.assertEqual(traj.preset, CameraMotionPreset.ORBIT_360)

    def test_montage_compiler_builds_timeline(self) -> None:
        timeline = OpenMontageCompiler.build_technical_launch_montage(
            project_name="Apex-Kernel",
            problem_statement="NP-hard latency bottleneck",
            primary_benchmark="p50=42us",
            architecture_focus="6-tier DAG pipeline",
            install_command="pip install apex-kernel",
        )
        self.assertEqual(len(timeline.shots), 4)
        self.assertEqual(timeline.total_duration_sec, 15.0)
        self.assertGreater(timeline.average_shot_length_sec, 2.0)

    def test_manifest_export_remotion_and_videoclaw(self) -> None:
        timeline = OpenMontageCompiler.build_technical_launch_montage(
            project_name="Apex-Kernel",
            problem_statement="Bottleneck",
            primary_benchmark="p50=42us",
            architecture_focus="DAG",
            install_command="pip install apex-kernel",
        )
        remotion = VideoManifestExporter.to_remotion_manifest(timeline)
        self.assertEqual(remotion["compositionId"], "ApexTechnicalLaunchTrailer")
        self.assertEqual(len(remotion["scenes"]), 4)

        vclaw = VideoManifestExporter.to_videoclaw_recipe(timeline)
        self.assertEqual(vclaw["target_resolution"], "1080p")
        self.assertEqual(len(vclaw["timeline"]), 4)


if __name__ == "__main__":
    unittest.main()
