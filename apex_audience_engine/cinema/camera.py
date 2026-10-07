"""Higgsfield-Inspired 3D Camera Trajectories & Motion Primitives.

Defines deterministic mathematical 3D camera vectors (position, orientation, optics)
for cinematic technical video direction, eliminating floaty and unnatural AI camera drift.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from typing import List, Tuple


class CameraMotionPreset(str, Enum):
    SLOW_DOLLY_PUSH_IN = "slow_dolly_push_in"
    ORBIT_360 = "orbit_360"
    WHIP_PAN = "whip_pan"
    RACK_FOCUS = "rack_focus"
    CRANE_UP = "crane_up"
    STATIC_METRIC_HOLD = "static_metric_hold"


@dataclass
class CameraKeyframe:
    timestamp_sec: float
    # 3D Spatial coordinates (meters)
    x: float
    y: float
    z: float
    # Rotation (degrees)
    pitch: float  # Tilt up/down
    yaw: float    # Pan left/right
    roll: float   # Dutch angle
    # Optics
    focal_length_mm: float
    aperture_f_stop: float
    focus_distance_m: float


@dataclass
class CameraTrajectory:
    name: str
    preset: CameraMotionPreset
    duration_sec: float
    keyframes: list[CameraKeyframe]

    def interpolate(self, t: float) -> CameraKeyframe:
        """Linear interpolation of camera keyframes at arbitrary timestamp t."""
        if not self.keyframes:
            return CameraKeyframe(0, 0, 0, 0, 0, 0, 0, 50, 2.8, 1.5)
        if t <= self.keyframes[0].timestamp_sec:
            return self.keyframes[0]
        if t >= self.keyframes[-1].timestamp_sec:
            return self.keyframes[-1]

        # Find keyframe pair
        for i in range(len(self.keyframes) - 1):
            k0 = self.keyframes[i]
            k1 = self.keyframes[i + 1]
            if k0.timestamp_sec <= t <= k1.timestamp_sec:
                factor = (t - k0.timestamp_sec) / (k1.timestamp_sec - k0.timestamp_sec)
                return CameraKeyframe(
                    timestamp_sec=t,
                    x=k0.x + factor * (k1.x - k0.x),
                    y=k0.y + factor * (k1.y - k0.y),
                    z=k0.z + factor * (k1.z - k0.z),
                    pitch=k0.pitch + factor * (k1.pitch - k0.pitch),
                    yaw=k0.yaw + factor * (k1.yaw - k0.yaw),
                    roll=k0.roll + factor * (k1.roll - k0.roll),
                    focal_length_mm=k0.focal_length_mm + factor * (k1.focal_length_mm - k0.focal_length_mm),
                    aperture_f_stop=k0.aperture_f_stop + factor * (k1.aperture_f_stop - k0.aperture_f_stop),
                    focus_distance_m=k0.focus_distance_m + factor * (k1.focus_distance_m - k0.focus_distance_m),
                )
        return self.keyframes[-1]


class CameraDirector:
    """Synthesizes smooth, physically grounded Higgsfield-style camera motions."""

    @staticmethod
    def generate_trajectory(preset: CameraMotionPreset, duration_sec: float = 3.0) -> CameraTrajectory:
        """Builds a trajectory with deterministic keyframes."""
        kfs: list[CameraKeyframe] = []

        if preset == CameraMotionPreset.SLOW_DOLLY_PUSH_IN:
            # Starts 2.0m away, pushes in to 1.2m on the terminal/code
            kfs.append(CameraKeyframe(0.0, x=0.0, y=0.0, z=2.0, pitch=0.0, yaw=0.0, roll=0.0, focal_length_mm=35.0, aperture_f_stop=2.0, focus_distance_m=2.0))
            kfs.append(CameraKeyframe(duration_sec, x=0.0, y=0.0, z=1.2, pitch=0.0, yaw=0.0, roll=0.0, focal_length_mm=35.0, aperture_f_stop=1.8, focus_distance_m=1.2))

        elif preset == CameraMotionPreset.ORBIT_360:
            # Circular orbit around center point (radius 2.5m)
            steps = 4
            for s in range(steps + 1):
                t = (s / steps) * duration_sec
                angle = (s / steps) * (2 * math.pi)
                x = 2.5 * math.sin(angle)
                z = 2.5 * math.cos(angle)
                yaw = -(angle * 180 / math.pi)
                kfs.append(CameraKeyframe(t, x=round(x, 3), y=0.5, z=round(z, 3), pitch=-10.0, yaw=round(yaw, 1), roll=0.0, focal_length_mm=50.0, aperture_f_stop=2.8, focus_distance_m=2.5))

        elif preset == CameraMotionPreset.RACK_FOCUS:
            # Fixed position, shifts focal distance from foreground (0.8m) to background metric (3.0m)
            kfs.append(CameraKeyframe(0.0, x=0.0, y=0.0, z=1.5, pitch=0.0, yaw=0.0, roll=0.0, focal_length_mm=85.0, aperture_f_stop=1.4, focus_distance_m=0.8))
            kfs.append(CameraKeyframe(duration_sec, x=0.0, y=0.0, z=1.5, pitch=0.0, yaw=0.0, roll=0.0, focal_length_mm=85.0, aperture_f_stop=1.4, focus_distance_m=3.0))

        elif preset == CameraMotionPreset.WHIP_PAN:
            # Fast snap pan 45 degrees
            kfs.append(CameraKeyframe(0.0, x=0.0, y=0.0, z=1.5, pitch=0.0, yaw=-25.0, roll=0.0, focal_length_mm=35.0, aperture_f_stop=2.8, focus_distance_m=1.5))
            kfs.append(CameraKeyframe(duration_sec, x=0.0, y=0.0, z=1.5, pitch=0.0, yaw=25.0, roll=2.0, focal_length_mm=35.0, aperture_f_stop=2.8, focus_distance_m=1.5))

        elif preset == CameraMotionPreset.CRANE_UP:
            # Ascending vertical pedestal
            kfs.append(CameraKeyframe(0.0, x=0.0, y=0.0, z=2.0, pitch=0.0, yaw=0.0, roll=0.0, focal_length_mm=28.0, aperture_f_stop=4.0, focus_distance_m=2.0))
            kfs.append(CameraKeyframe(duration_sec, x=0.0, y=1.5, z=2.5, pitch=-20.0, yaw=0.0, roll=0.0, focal_length_mm=28.0, aperture_f_stop=4.0, focus_distance_m=2.8))

        else:  # STATIC_METRIC_HOLD
            kfs.append(CameraKeyframe(0.0, x=0.0, y=0.0, z=1.5, pitch=0.0, yaw=0.0, roll=0.0, focal_length_mm=50.0, aperture_f_stop=2.8, focus_distance_m=1.5))
            kfs.append(CameraKeyframe(duration_sec, x=0.0, y=0.0, z=1.5, pitch=0.0, yaw=0.0, roll=0.0, focal_length_mm=50.0, aperture_f_stop=2.8, focus_distance_m=1.5))

        return CameraTrajectory(
            name=preset.value,
            preset=preset,
            duration_sec=duration_sec,
            keyframes=kfs,
        )
