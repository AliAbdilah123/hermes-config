import React from "react";
import { Composition, getInputProps, registerRoot } from "remotion";
import { FONT } from "./fonts";
import { Reel } from "./Reel";
import { DEFAULT_THEME, Timeline } from "./types";

const input = getInputProps() as Partial<Timeline>;
void FONT; // ensure the font module is bundled and loaded before render

// Duration comes from --props (work/timeline.json). Fallback keeps
// `remotion studio` usable before the first pipeline run.
const timeline: Timeline = {
  slug: "reel", title: "Reel", fps: 30, width: 1080, height: 1920,
  duration: 6, theme: DEFAULT_THEME,
  scenes: [{
    id: "s1", kind: "hook", kicker: "preview", headline: "Run the pipeline",
    body: "scripts/reel.py init + tts + timeline", say: "", audio: "",
    start: 0, dur: 6, cues: [{ start: 0, end: 3, text: "props not loaded" }],
  }],
  ...input,
};

export const Root: React.FC = () => (
  <Composition
    id="Reel"
    component={Reel}
    durationInFrames={Math.max(1, Math.round(timeline.duration * timeline.fps))}
    fps={timeline.fps}
    width={timeline.width}
    height={timeline.height}
    defaultProps={timeline}
  />
);

registerRoot(Root);