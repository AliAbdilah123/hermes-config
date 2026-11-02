# Remotion CLI invariants (each one cost a debugging cycle)

Verified on Remotion 4.0.539, Node 22, ARM64 Linux.

## 1. Entry point must call `registerRoot()`

Symptom:

```
Error: You passed src/index.tsx as your entry point, but this file does not
contain "registerRoot".
```

A file that only exports `Root` is not a valid entry point. The last line of
the entry file must be:

```ts
registerRoot(Root);
```

`remotion studio` sometimes tolerates the omission; `remotion render` /
`compositions` never do. Add it every time.

## 2. `loadFont()` must be called at module scope of the entry graph

Symptom: bundling completes, then

```
Error: A delayRender() "Loading root component" was called but not cleared
after 28000ms
```

Cause: `import "./fonts"` as a bare side-effect import, or calling `loadFont()`
inside a component. `loadFont()` calls `delayRender()` and needs the module to
be evaluated before the root renders.

Correct:

```ts
// fonts.ts
import { loadFont } from "@remotion/google-fonts/Inter";
export const { fontFamily: FONT } = loadFont("normal", {
  weights: ["500", "600", "800"], subsets: ["latin"],
  ignoreTooManyRequestsWarning: true,
});
```

```ts
// index.tsx
import { FONT } from "./fonts";
void FONT;   // forces the module into the bundle before root render
```

Keep the weight list tight — every extra weight is extra network requests per
render, and ≥20 triggers Remotion's warning (silence it with
`ignoreTooManyRequestsWarning: true`).

## 3. `--props` must be an absolute path

Symptom:

```
You passed --props but it was neither valid JSON nor a file path to a valid
JSON file. Provided value: work/timeline.json
```

Remotion resolves the props path against the **CLI's** cwd, not the project
directory. Always pass `Path(...).resolve()`. Inline JSON also works but breaks
on long scripts (shell quoting, arg length) — use the file.

Corollary: a *missing* props file produces a different, confusing error than a
*found* one — if a stage writes `timeline.json` and the next command claims it
"isn't valid JSON", check existence before debugging the JSON.

## 4. Composition duration must come from props, not a constant

```tsx
const tl = { ...FALLBACK, ...(getInputProps() as Partial<Timeline>) };
<Composition id="Reel" component={Reel}
  durationInFrames={Math.max(1, Math.round(tl.duration * tl.fps))}
  fps={tl.fps} width={tl.width} height={tl.height} defaultProps={tl} />
```

Keep a small fallback object so `remotion studio` opens before the first
pipeline run. Verified output: 22.52 s of timeline → 22.53 s rendered (±1
frame) at 1080×1920, `--concurrency=2`, ~73 s wall clock.

## Misc

- `--log=error` keeps render output to one line; without it the progress bar
  floods any log stream you're piping (SSE, cron, background job).
- `npx remotion still src/index.tsx Reel out/f.png --props=<abs> --frame=45`
  is the cheapest way to check a layout — one frame instead of a full render.
- Reuse an existing `node_modules` by symlinking it into the new project;
  `remotion`/`@remotion/cli` resolve fine through a symlink and it avoids a
  multi-minute install per reel.
- `tsconfig.json` needs `"jsx": "react-jsx"`, `"esModuleInterop": true`,
  `"skipLibCheck": true`, `"moduleResolution": "bundler"`.