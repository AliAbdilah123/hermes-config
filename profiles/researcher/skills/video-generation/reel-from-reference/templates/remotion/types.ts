export type Cue = { start: number; end: number; text: string };
export type Scene = {
  id: string; kind: "hook" | "point" | "stat" | "list" | "end" | string;
  kicker: string; headline: string; body: string; say: string;
  audio: string; start: number; dur: number; cues: Cue[];
};
export type Theme = {
  bg: string; fg: string; dim: string; accent: string; accent2: string;
  font: string;
};
export type Timeline = {
  slug: string; title: string; fps: number; width: number; height: number;
  duration: number; theme: Theme; scenes: Scene[];
};

export const DEFAULT_THEME: Theme = {
  bg: "#0B0F14", fg: "#F4F1EA", dim: "#8A93A0", accent: "#FFB300",
  accent2: "#4ADE80", font: "Inter",
};