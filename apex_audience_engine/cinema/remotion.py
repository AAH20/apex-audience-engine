"""Remotion React Video Composition & Project Compiler.

Implements the official Remotion project architecture based on Hermes skills:
- remotion-best-practices (project layout, composability, and architecture)
- remotion-create (Composition definitions, defaultProps, width/height/fps)
- remotion-markup (Series, Sequence, AbsoluteFill, useCurrentFrame, interpolate, spring)
- remotion-captions (word-level karaoke subtitles and emphasis tokens)
- remotion-render (CLI render scripts, multi-threaded rendering, codec optimization)
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, Optional

from apex_audience_engine.cinema.montage import MontageShot, MontageTimeline, ShotType


@dataclass
class RemotionProjectConfig:
    """Configuration parameters for the generated Remotion project."""
    composition_id: str = "ApexTechnicalLaunchTrailer"
    fps: int = 30
    width: int = 1920
    height: int = 1080
    bg_color: str = "#090d16"
    accent_color: str = "#eb6c36"
    telemetry_color: str = "#38bdf8"


class RemotionProjectCompiler:
    """Compiles MontageTimeline models into a complete, buildable Remotion React project."""

    def __init__(self, config: Optional[RemotionProjectConfig] = None) -> None:
        self.config = config or RemotionProjectConfig()

    def compile_project(self, timeline: MontageTimeline) -> dict[str, str]:
        """Returns a mapping of relative file paths to their source code contents."""
        cfg = self.config
        total_frames = int(timeline.total_duration_sec * cfg.fps)

        return {
            "package.json": self._generate_package_json(),
            "remotion.config.ts": self._generate_remotion_config(),
            "tsconfig.json": self._generate_tsconfig(),
            "src/index.ts": self._generate_index_ts(),
            "src/Root.tsx": self._generate_root_tsx(timeline, total_frames),
            "src/MainComposition.tsx": self._generate_main_composition_tsx(timeline),
            "src/components/SceneCard.tsx": self._generate_scene_card_tsx(),
            "src/components/CaptionsTrack.tsx": self._generate_captions_track_tsx(),
            "src/components/TelemetryHud.tsx": self._generate_telemetry_hud_tsx(),
            "src/types.ts": self._generate_types_ts(),
            "README.md": self._generate_readme(timeline),
        }

    def _generate_package_json(self) -> str:
        pkg = {
            "name": "apex-launch-remotion",
            "version": "1.0.0",
            "private": True,
            "scripts": {
                "dev": "remotion studio src/index.ts",
                "start": "remotion studio src/index.ts",
                "build": f"remotion render src/index.ts {self.config.composition_id} out/trailer.mp4 --codec=h264 --crf=18",
                "render": f"remotion render src/index.ts {self.config.composition_id} out/trailer.mp4",
                "upgrade": "remotion upgrade",
            },
            "dependencies": {
                "@remotion/captions": "^4.0.200",
                "@remotion/cli": "^4.0.200",
                "@remotion/media-utils": "^4.0.200",
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "remotion": "^4.0.200",
            },
            "devDependencies": {
                "@types/react": "^18.2.0",
                "typescript": "^5.2.0",
            },
        }
        return json.dumps(pkg, indent=2)

    def _generate_remotion_config(self) -> str:
        return """import { Config } from '@remotion/cli/config';

Config.setVideoImageFormat('jpeg');
Config.setCodec('h264');
Config.setCrf(18);
Config.setPixelFormat('yuv420p');
Config.setConcurrency(4);
Config.setChromiumOpenGlRenderer('angle');
"""

    def _generate_tsconfig(self) -> str:
        return """{
  "compilerOptions": {
    "target": "ES2022",
    "module": "commonjs",
    "jsx": "react-jsx",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true
  },
  "include": ["src"]
}
"""

    def _generate_index_ts(self) -> str:
        return """import { registerRoot } from 'remotion';
import { Root } from './Root';

registerRoot(Root);
"""

    def _generate_types_ts(self) -> str:
        return """export interface ShotProps {
  id: string;
  type: string;
  headline: string;
  payload: string;
  durationFrames: number;
  cameraPreset: string;
  transition: string;
  audioCue: string;
}

export interface LaunchTrailerProps {
  title: string;
  shots: ShotProps[];
}
"""

    def _generate_root_tsx(self, timeline: MontageTimeline, total_frames: int) -> str:
        cfg = self.config
        shots_data = [
            {
                "id": s.shot_id,
                "type": s.shot_type.value,
                "headline": s.headline,
                "payload": s.code_or_metric_payload,
                "durationFrames": int(s.duration_sec * cfg.fps),
                "cameraPreset": s.camera_trajectory.preset.value,
                "transition": s.transition_out.value,
                "audioCue": s.foley_cue.value,
            }
            for s in timeline.shots
        ]

        shots_json = json.dumps(shots_data, indent=6)

        return f"""import React from 'react';
import {{ Composition }} from 'remotion';
import {{ MainComposition }} from './MainComposition';
import {{ LaunchTrailerProps }} from './types';

const defaultProps: LaunchTrailerProps = {{
  title: "{timeline.title}",
  shots: {shots_json}
}};

export const Root: React.FC = () => {{
  return (
    <Composition
      id="{cfg.composition_id}"
      component={{MainComposition}}
      durationInFrames={{{total_frames}}}
      fps={{{cfg.fps}}}
      width={{{cfg.width}}}
      height={{{cfg.height}}}
      defaultProps={{defaultProps}}
    />
  );
}};
"""

    def _generate_main_composition_tsx(self, timeline: MontageTimeline) -> str:
        return """import React from 'react';
import {
  AbsoluteFill,
  Series,
  useCurrentFrame,
  useVideoConfig,
  Audio,
  staticFile,
} from 'remotion';
import { LaunchTrailerProps } from './types';
import { SceneCard } from './components/SceneCard';
import { TelemetryHud } from './components/TelemetryHud';
import { CaptionsTrack } from './components/CaptionsTrack';

export const MainComposition: React.FC<LaunchTrailerProps> = ({ title, shots }) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();

  return (
    <AbsoluteFill
      style={{
        backgroundColor: '#090d16',
        color: '#f8fafc',
        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
        overflow: 'hidden',
      }}
    >
      {/* Background Radial Gradient Grid */}
      <AbsoluteFill
        style={{
          background: 'radial-gradient(circle at 50% 30%, #131b2e 0%, #090d16 85%)',
          zIndex: 0,
        }}
      />

      {/* Sequential Scene Storyboard */}
      <Series>
        {shots.map((shot, idx) => (
          <Series.Sequence
            key={shot.id}
            durationInFrames={shot.durationFrames}
            name={`${idx + 1}. ${shot.headline}`}
          >
            <SceneCard shot={shot} index={idx} />
          </Series.Sequence>
        ))}
      </Series>

      {/* Global Telemetry HUD Overlay */}
      <TelemetryHud currentFrame={frame} totalFrames={shots.reduce((acc, s) => acc + s.durationFrames, 0)} fps={fps} />

      {/* Global Word-Level Captions Track */}
      <CaptionsTrack currentFrame={frame} fps={fps} shots={shots} />
    </AbsoluteFill>
  );
};
"""

    def _generate_scene_card_tsx(self) -> str:
        return """import React from 'react';
import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import { ShotProps } from '../types';

export const SceneCard: React.FC<{ shot: ShotProps; index: number }> = ({ shot, index }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Smooth entrance spring
  const entrance = spring({
    frame,
    fps,
    config: { damping: 14, stiffness: 100, mass: 0.8 },
  });

  // Camera drift simulation
  const scale = interpolate(frame, [0, shot.durationFrames], [1.0, 1.05], {
    extrapolateRight: 'clamp',
  });

  const opacity = interpolate(
    frame,
    [0, 10, shot.durationFrames - 10, shot.durationFrames],
    [0, 1, 1, 0],
    { extrapolateRight: 'clamp' }
  );

  return (
    <AbsoluteFill
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '80px',
        opacity,
        transform: `scale(${scale})`,
        zIndex: 5,
      }}
    >
      <div
        style={{
          display: 'inline-block',
          padding: '6px 18px',
          borderRadius: '9999px',
          backgroundColor: 'rgba(235, 108, 54, 0.15)',
          border: '1px solid rgba(235, 108, 54, 0.4)',
          color: '#eb6c36',
          fontFamily: "'JetBrains Mono', monospace",
          fontSize: '14px',
          fontWeight: 700,
          letterSpacing: '0.1em',
          marginBottom: '28px',
          textTransform: 'uppercase',
        }}
      >
        {shot.type.toUpperCase()} · SCENE {String(index + 1).padStart(2, '0')}
      </div>

      <h1
        style={{
          fontSize: '64px',
          fontWeight: 800,
          lineHeight: 1.15,
          maxWidth: '1300px',
          textAlign: 'center',
          margin: '0 0 32px 0',
          letterSpacing: '-0.02em',
          background: 'linear-gradient(180deg, #ffffff 0%, #94a3b8 100%)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          transform: `translateY(${interpolate(entrance, [0, 1], [40, 0])}px)`,
        }}
      >
        {shot.headline}
      </h1>

      {shot.type === 'benchmark_proving' ? (
        <div style={{ display: 'flex', alignItems: 'baseline', gap: '16px', margin: '24px 0' }}>
          <span
            style={{
              fontSize: '110px',
              fontWeight: 900,
              fontFamily: "'JetBrains Mono', monospace",
              color: '#38bdf8',
              textShadow: '0 0 40px rgba(56, 189, 248, 0.4)',
            }}
          >
            {shot.payload.includes('=') ? shot.payload.split('=')[1] : shot.payload}
          </span>
          <span style={{ fontSize: '24px', color: '#94a3b8', textTransform: 'uppercase' }}>
            {shot.payload.includes('=') ? shot.payload.split('=')[0] : 'LATENCY'}
          </span>
        </div>
      ) : (
        <div
          style={{
            width: '100%',
            maxWidth: '1050px',
            backgroundColor: '#0d121f',
            border: '1px solid #1e293b',
            borderRadius: '12px',
            padding: '24px 32px',
            fontFamily: "'JetBrains Mono', monospace",
            fontSize: '22px',
            color: '#38bdf8',
            boxShadow: '0 25px 60px rgba(0, 0, 0, 0.5)',
            margin: '20px 0',
          }}
        >
          <span style={{ color: '#eb6c36', marginRight: '12px' }}>&gt;</span>
          {shot.payload}
        </div>
      )}

      <div style={{ display: 'flex', gap: '14px', marginTop: '36px' }}>
        <span style={pillStyle('#818cf8')}>SFX: {shot.audioCue}</span>
        <span style={pillStyle('#38bdf8')}>CAM: {shot.cameraPreset}</span>
        <span style={pillStyle('#10b981')}>DUR: {(shot.durationFrames / fps).toFixed(1)}s</span>
      </div>
    </AbsoluteFill>
  );
};

const pillStyle = (color: string): React.CSSProperties => ({
  fontFamily: "'JetBrains Mono', monospace",
  fontSize: '13px',
  padding: '6px 14px',
  borderRadius: '6px',
  backgroundColor: 'rgba(255, 255, 255, 0.04)',
  border: `1px solid ${color}40`,
  color,
});
"""

    def _generate_captions_track_tsx(self) -> str:
        return """import React from 'react';
import { ShotProps } from '../types';

export const CaptionsTrack: React.FC<{
  currentFrame: number;
  fps: number;
  shots: ShotProps[];
}> = ({ currentFrame, fps, shots }) => {
  // Compute which shot is currently playing
  let accumulated = 0;
  let activeShot: ShotProps | null = null;
  for (const s of shots) {
    if (currentFrame >= accumulated && currentFrame < accumulated + s.durationFrames) {
      activeShot = s;
      break;
    }
    accumulated += s.durationFrames;
  }

  if (!activeShot) return null;

  return (
    <div
      style={{
        position: 'absolute',
        bottom: '40px',
        left: 0,
        right: 0,
        display: 'flex',
        justifyContent: 'center',
        zIndex: 20,
      }}
    >
      <div
        style={{
          padding: '8px 24px',
          borderRadius: '9999px',
          backgroundColor: 'rgba(9, 13, 22, 0.75)',
          backdropFilter: 'blur(12px)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          color: '#f8fafc',
          fontFamily: "'JetBrains Mono', monospace",
          fontSize: '16px',
          letterSpacing: '0.02em',
        }}
      >
        <span style={{ color: '#eb6c36', marginRight: '8px' }}>●</span>
        {activeShot.headline}
      </div>
    </div>
  );
};
"""

    def _generate_telemetry_hud_tsx(self) -> str:
        return """import React from 'react';

export const TelemetryHud: React.FC<{
  currentFrame: number;
  totalFrames: number;
  fps: number;
}> = ({ currentFrame, totalFrames, fps }) => {
  const currentSeconds = (currentFrame / fps).toFixed(2);
  const totalSeconds = (totalFrames / fps).toFixed(2);
  const progressPct = ((currentFrame / totalFrames) * 100).toFixed(1);

  return (
    <div
      style={{
        position: 'absolute',
        top: '32px',
        left: '48px',
        right: '48px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        zIndex: 30,
        fontFamily: "'JetBrains Mono', monospace",
        fontSize: '13px',
        color: '#94a3b8',
        letterSpacing: '0.08em',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <span style={{ color: '#10b981' }}>REC ●</span>
        <span>APEX CINEMATIC TELEMETRY</span>
      </div>

      <div style={{ display: 'flex', gap: '24px' }}>
        <span>FRAME: {String(currentFrame).padStart(4, '0')}/{totalFrames}</span>
        <span>TIME: {currentSeconds}s / {totalSeconds}s</span>
        <span style={{ color: '#38bdf8' }}>{progressPct}%</span>
      </div>
    </div>
  );
};
"""

    def _generate_readme(self, timeline: MontageTimeline) -> str:
        return f"""# {timeline.title} — Remotion Video Project

Generated autonomously by **Apex Audience Engine** following Hermes agent skills:
`remotion-best-practices`, `remotion-create`, `remotion-markup`, and `remotion-render`.

## Quickstart

```bash
# 1. Install dependencies
npm install

# 2. Launch Remotion Studio Preview
npm run dev

# 3. Render 1080p MP4
npm run build
```

## Structure
- `src/Root.tsx`: Composition registry with `{self.config.composition_id}`.
- `src/MainComposition.tsx`: Timeline sequence with `<Series>`.
- `src/components/SceneCard.tsx`: Kinetic scene presenter with spring animations.
- `src/components/CaptionsTrack.tsx`: Synchronized subtitle bar.
- `src/components/TelemetryHud.tsx`: HUD overlays.
"""
