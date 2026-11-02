import React from "react";
import {
  AbsoluteFill, Sequence, interpolate, spring, useCurrentFrame,
  useVideoConfig, Easing,
} from "remotion";
import { Scene, Theme, Timeline } from "./types";

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const ease = Easing.bezier(0.22, 1, 0.36, 1);

/** Kinetic line: words rise in, staggered, deterministic from local frame. */
const Words: React.FC<{
  text: string; delay?: number; size: number; color?: string; weight?: number;
  lineHeight?: number; accent?: string; highlight?: string[];
}> = ({ text, delay = 0, size, color, weight = 800, lineHeight = 1.04,
       accent = "#FFB300", highlight = [] }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <div style={{
      display: "flex", flexWrap: "wrap", gap: `0 ${size * 0.24}px`,
      fontFamily: "Inter, sans-serif", fontSize: size, fontWeight: weight,
      lineHeight, letterSpacing: "-0.02em", color, textTransform: "uppercase",
    }}>
      {text.split(/\s+/).filter(Boolean).map((w, i) => {
        const p = spring({ frame: frame - delay - i * 2.2, fps, config: { damping: 200 } });
        const hot = highlight.some((h) => w.toLowerCase().includes(h.toLowerCase()));
        return (
          <span key={i} style={{
            display: "inline-block", opacity: p,
            transform: `translateY(${(1 - p) * size * 0.34}px)`,
            color: hot ? accent : color,
          }}>{w}</span>
        );
      })}
    </div>
  );
};

const Bar: React.FC<{ theme: Theme; p: number }> = ({ theme, p }) => (
  <div style={{
    position: "absolute", left: 96, bottom: 96, width: 888, height: 6,
    background: "rgba(255,255,255,0.10)", borderRadius: 3, overflow: "hidden",
  }}>
    <div style={{
      width: `${Math.max(0.02, Math.min(1, p)) * 100}%`, height: "100%",
      background: theme.accent,
    }} />
  </div>
);

const Cue: React.FC<{ text: string; theme: Theme }> = ({ text, theme }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = spring({ frame, fps, config: { damping: 260, stiffness: 140 } });
  return (
    <div style={{
      position: "absolute", left: 96, right: 96, bottom: 264,
      display: "flex", justifyContent: "center",
    }}>
      <div style={{
        background: "rgba(6,9,13,0.78)", backdropFilter: "blur(6px)",
        borderLeft: `6px solid ${theme.accent}`, borderRadius: 10,
        padding: "20px 28px", maxWidth: 860,
        fontFamily: "Inter, sans-serif", fontSize: 46, lineHeight: 1.24,
        fontWeight: 600, color: theme.fg,
        opacity: p, transform: `translateY(${(1 - p) * 18}px)`,
      }}>{text}</div>
    </div>
  );
};

const SceneView: React.FC<{ scene: Scene; theme: Theme; index: number; count: number; totalDur: number }> =
  ({ scene, theme, index, count, totalDur }) => {
    const frame = useCurrentFrame();
    const { fps, durationInFrames } = useVideoConfig();
    const dur = durationInFrames / fps;
    const enter = interpolate(frame, [0, 0.45 * fps], [0, 1], { ...clamp, easing: ease });
    const exit = interpolate(frame, [dur * fps - 0.3 * fps, dur * fps], [1, 0], clamp);
    const cue = scene.cues.find((c) => {
      const t = frame / fps + scene.start;
      return t >= c.start - 0.05 && t <= c.end + 0.18;
    });
    // slow push-in: 100% -> 103% over the scene, never more
    const push = interpolate(frame, [0, durationInFrames], [1, 1.03], clamp);

    return (
      <AbsoluteFill style={{
        background: theme.bg, color: theme.fg, overflow: "hidden",
        opacity: Math.min(enter, exit),
      }}>
        <AbsoluteFill style={{
          transform: `scale(${push})`,
          background: `radial-gradient(900px 700px at 82% 12%, ${theme.accent}1F, transparent 70%),
                       radial-gradient(700px 700px at 12% 88%, ${theme.accent2}14, transparent 72%)`,
        }} />
        {/* hairline frame */}
        <div style={{
          position: "absolute", inset: 56, border: "1px solid rgba(255,255,255,0.10)",
          borderRadius: 4, transform: `scaleX(${enter})`, transformOrigin: "left",
        }} />

        {/* top: kicker + scene index */}
        <div style={{
          position: "absolute", top: 132, left: 96, right: 96,
          display: "flex", justifyContent: "space-between", alignItems: "baseline",
          fontFamily: "Inter, sans-serif", fontSize: 30, letterSpacing: "0.16em",
          textTransform: "uppercase", fontWeight: 700, opacity: enter,
        }}>
          <span style={{ color: theme.accent }}>{scene.kicker || "REEL"}</span>
          <span style={{ color: theme.dim }}>
            {String(index + 1).padStart(2, "0")}/{String(count).padStart(2, "0")}
          </span>
        </div>

        {scene.kind === "stat" ? (
          <div style={{
            position: "absolute", top: 520, left: 96, right: 96,
            fontFamily: "Inter, sans-serif",
          }}>
            <div style={{
              fontSize: 300, fontWeight: 900, lineHeight: 0.86, letterSpacing: "-0.05em",
              color: theme.accent,
              transform: `scale(${spring({ frame: frame - 6, fps, config: { damping: 200 } })})`,
              transformOrigin: "left bottom",
            }}>{scene.headline}</div>
            <div style={{ height: 10, width: 220, background: theme.fg, marginTop: 34,
              transform: `scaleX(${enter})`, transformOrigin: "left" }} />
            <div style={{
              marginTop: 36, fontSize: 62, fontWeight: 600, lineHeight: 1.16,
              color: theme.fg, maxWidth: 820,
            }}>{scene.body}</div>
          </div>
        ) : (
          <div style={{
            position: "absolute", top: scene.kind === "hook" ? 700 : 560,
            left: 96, right: 96,
          }}>
            <Words text={scene.headline} size={scene.kind === "hook" ? 122 : 96}
              delay={4} color={theme.fg} accent={theme.accent} />
            {scene.body ? (
              <div style={{
                marginTop: 44, fontFamily: "Inter, sans-serif", fontSize: 46,
                lineHeight: 1.36, fontWeight: 500, color: theme.dim, maxWidth: 820,
                opacity: interpolate(frame, [0.5 * fps, 0.9 * fps], [0, 1], clamp),
              }}>{scene.body}</div>
            ) : null}
          </div>
        )}

        {cue ? <Cue text={cue.text} theme={theme} /> : null}
        <Bar theme={theme} p={(scene.start + frame / fps) / totalDur} />
      </AbsoluteFill>
    );
  };

export const Reel: React.FC<Timeline> = ({ scenes, theme, duration }) => {
  const { fps } = useVideoConfig();
  return (
    <AbsoluteFill style={{ background: theme.bg }}>
      {scenes.map((sc, i) => (
        <Sequence key={sc.id} from={Math.round(sc.start * fps)}
          durationInFrames={Math.max(1, Math.round(sc.dur * fps))} name={sc.id}>
          <SceneView scene={sc} theme={theme} index={i} count={scenes.length}
            totalDur={duration} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};