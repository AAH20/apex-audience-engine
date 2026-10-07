"""Cinema Subsystem — Higgsfield 3D Camera, Open Montage, HyperFrames, Remotion, and GIF Automation."""

from apex_audience_engine.cinema.camera import (
    CameraDirector,
    CameraKeyframe,
    CameraMotionPreset,
    CameraTrajectory,
)
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
from apex_audience_engine.cinema.manifest import VideoManifestExporter
from apex_audience_engine.cinema.montage import (
    CutTransition,
    FoleyCue,
    MontageShot,
    MontageTimeline,
    OpenMontageCompiler,
    ShotType,
)
from apex_audience_engine.cinema.remotion import (
    RemotionProjectCompiler,
    RemotionProjectConfig,
)

__all__ = [
    "CameraDirector",
    "CameraKeyframe",
    "CameraMotionPreset",
    "CameraTrajectory",
    "MontageShot",
    "MontageTimeline",
    "OpenMontageCompiler",
    "ShotType",
    "CutTransition",
    "FoleyCue",
    "VideoManifestExporter",
    "HyperFramesCompiler",
    "HyperFramesOptions",
    "HyperFramesTheme",
    "RemotionProjectCompiler",
    "RemotionProjectConfig",
    "ScreenshotsToGifPipeline",
    "GifPipelineOptions",
    "GifCaptureRoute",
    "PurePythonGifGenerator",
]
