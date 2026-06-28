# Video Slicer Editor Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task after review.

**Goal:** Build a web-only MVP video editor with basic editing features plus a slice workflow that can split one uploaded video into multiple exported clips using typed timestamps or the current playhead position.

**Architecture:** Build the MVP as a browser-only, local-first editor so users can upload, slice, and export videos without account setup or cloud storage. Use FFmpeg.wasm for client-side processing, target 10-minute videos as the safe default, and allow an experimental 30-minute path only when the browser/device passes capability checks.

**Tech Stack:** React + Vite + TypeScript, shadcn/ui, Tailwind CSS, Zustand, FFmpeg.wasm, WebCodecs where supported, IndexedDB/localStorage for local project persistence, JSZip for ZIP export.

---

## 1. Product Scope

### MVP Features
- Import video from local file.
- Play/pause, scrub timeline, frame/time display.
- Set slice start/end manually via timestamp inputs.
- Set slice start/end from current playhead position.
- Maintain a slice list with names, start/end, duration, reorder/delete/edit actions.
- Preview selected slice.
- Export every slice as separate video files in a batch.
- Export both individual files and a ZIP bundle.
- Local-only project persistence; no login or cloud storage in MVP.
- Frame-accurate slicing from day 1 where technically possible, using re-encoding/keyframe-aware export instead of copy-only cuts when exactness is requested.
- Basic editor operations: trim, split, mute audio, simple crop/resize preset, export quality preset.

### Later Features
- Multi-track timeline.
- Captions/subtitles.
- Text/image overlays.
- Transitions.
- Cloud rendering queue.
- Collaborative review links.
- Templates for TikTok/Reels/YouTube Shorts.

## 2. Core User Journey

1. User uploads a source video.
2. App displays video preview and timeline.
3. User moves playhead to the desired segment start and clicks **Use Current Time as Start**.
4. User moves playhead to the desired segment end and clicks **Use Current Time as End**.
5. User names the slice and clicks **Add Slice**.
6. User repeats for multiple clips or types exact timestamps directly.
7. User clicks **Export All Slices**.
8. App renders both individual downloadable files and a ZIP bundle.

## 3. Suggested Information Architecture

- `Dashboard`: recent projects, create/import project.
- `Editor`: preview, timeline, slice builder, slice list, export panel.
- `Export History`: rendered clips and downloadable assets.
- `Settings`: default export format, quality, shortcut preferences.

## 4. Data Model

```ts
type VideoProject = {
  id: string;
  name: string;
  sourceFileName: string;
  sourceDurationMs: number;
  slices: VideoSlice[];
  exportSettings: ExportSettings;
};

type VideoSlice = {
  id: string;
  label: string;
  startMs: number;
  endMs: number;
  muted?: boolean;
  cropPreset?: 'original' | '9:16' | '1:1' | '16:9';
};

type ExportSettings = {
  format: 'mp4' | 'webm';
  quality: 'draft' | 'standard' | 'high';
  accuracy: 'frame-accurate' | 'fast-keyframe';
  delivery: 'individual' | 'zip' | 'both';
  namingPattern: string;
};
```

## 4.1 MVP Decisions

- Platform: **web only for MVP**.
- Video length target: **10 minutes guaranteed path**, with **30 minutes experimental** if device memory/performance checks pass.
- Accuracy: **frame-accurate slicing from day 1** to avoid hard-to-rework export assumptions later.
- Download mode: **both individual clips and ZIP bundle**.
- Persistence: **local only** using browser storage; no accounts/cloud sync.

## 5. Slice Validation Rules

- `startMs >= 0`.
- `endMs <= sourceDurationMs`.
- `endMs > startMs`.
- Minimum duration: 250ms.
- Hard validation target: 10-minute source videos. Show warning and capability check for videos between 10 and 30 minutes.
- Warn, but do not block, overlapping slices.
- Prevent duplicate labels when exporting as individual files unless auto-numbering is enabled.
- Default export uses frame-accurate mode. Provide a future/advanced fast keyframe mode only if it is clearly labeled as less precise.

## 6. Implementation Tasks

### Task 1: Seed the project shell

**Objective:** Create the initial web app using the user’s standard boilerplate approach if this becomes an implementation task.

**Files:**
- Create/modify: `package.json`, `apps/web/src/main.tsx`, `apps/web/src/App.tsx`
- Create: `apps/web/src/pages/EditorPage.tsx`

**Verification:**
- `npm install`
- `npm run dev`
- Open the public app URL and verify the editor shell loads.

### Task 2: Build video import and playback

**Objective:** Let the user choose a local video and preview it in-browser.

**Files:**
- Create: `apps/web/src/features/video-import/VideoDropzone.tsx`
- Create: `apps/web/src/features/player/VideoPreview.tsx`
- Create: `apps/web/src/stores/editorStore.ts`

**Verification:**
- Upload an MP4.
- Confirm duration, current time, and play/pause state update correctly.

### Task 3: Add timeline and current-position controls

**Objective:** Provide scrubber and buttons to capture current playhead as slice start/end.

**Files:**
- Create: `apps/web/src/features/timeline/Timeline.tsx`
- Create: `apps/web/src/features/slices/SliceBuilder.tsx`
- Test: `apps/web/src/features/slices/sliceValidation.test.ts`

**Verification:**
- Move playhead, click **Set Start**, move again, click **Set End**.
- Confirm fields are populated in `HH:MM:SS.mmm` format.

### Task 4: Implement manual timestamp entry and slice list

**Objective:** Allow exact timestamp typing, validation, editing, deleting, and reordering.

**Files:**
- Create: `apps/web/src/lib/timecode.ts`
- Create: `apps/web/src/lib/sliceValidation.ts`
- Create: `apps/web/src/features/slices/SliceList.tsx`
- Test: `apps/web/src/lib/timecode.test.ts`

**Verification:**
- `00:01:05.500` parses to `65500` ms.
- Invalid ranges show inline errors.
- Multiple slices can be added and edited.

### Task 5: Add client-side FFmpeg export with frame-accurate slicing

**Objective:** Export each configured slice into separate video files using frame-accurate FFmpeg commands by default.

**Files:**
- Create: `apps/web/src/features/export/ffmpegClient.ts`
- Create: `apps/web/src/features/export/ExportPanel.tsx`
- Create: `apps/web/src/features/export/exportQueue.ts`

**Verification:**
- Add 2-3 slices.
- Export all.
- Download output files and verify durations match the slice ranges.
- Verify cuts around non-keyframe timestamps are accurate by re-encoding rather than stream-copying.

### Task 5.1: Add ZIP export bundle

**Objective:** Package exported clips into one ZIP while still keeping individual download links.

**Files:**
- Create: `apps/web/src/features/export/zipExport.ts`
- Modify: `apps/web/src/features/export/ExportPanel.tsx`

**Verification:**
- Export 2-3 slices.
- Confirm each clip has its own download button.
- Confirm ZIP download contains every clip with the expected filename.

### Task 6: Add basic editing features

**Objective:** Add mute audio, crop/resize preset, and quality preset support per export.

**Files:**
- Modify: `apps/web/src/features/slices/SliceBuilder.tsx`
- Modify: `apps/web/src/features/export/ffmpegClient.ts`
- Create: `apps/web/src/features/editing/BasicEditControls.tsx`

**Verification:**
- Export muted clip and confirm audio is removed.
- Export 9:16 preset and confirm dimensions.

### Task 7: Add local-only project persistence

**Objective:** Save project metadata and slice definitions locally without login/cloud storage.

**Files:**
- Create: `apps/web/src/lib/localProjects.ts`
- Modify: `apps/web/src/stores/editorStore.ts`

**Verification:**
- Create a project and several slices.
- Refresh browser.
- Confirm slice metadata and export settings restore locally.

## 7. Design System Direction

- Use shadcn/ui components for buttons, dialogs, inputs, tabs, dropdown menus, progress, toast notifications, and cards.
- Theme: dark editing-suite UI with high-contrast timeline accents.
- Primary actions: electric blue/purple gradient.
- Timeline: visible playhead, selected range highlight, slice color chips.
- Error states: inline timestamp validation and non-blocking warning panel.

## 8. Risks and Tradeoffs

- FFmpeg.wasm can be slow and memory-heavy for large videos; guarantee the UX around 10-minute videos first and gate 30-minute attempts behind a performance/memory warning.
- Browser codec support varies; standardize MVP export to MP4/WebM based on available FFmpeg build.
- Frame-accurate cuts require re-encoding in many cases, which is slower than keyframe-only stream copy.
- Local-only storage means projects stay on the device/browser and should warn users before clearing site data.

## 9. Resolved MVP Decisions

1. MVP is **web only**.
2. Target **10-minute videos by default**; allow **30-minute experimental mode** if not too heavy for typical phones.
3. Support **frame-accurate slicing from day 1**.
4. Support **both individual downloads and ZIP export**.
5. Persist projects **locally only** for now.

## 10. Acceptance Criteria

- A user can import a single video.
- A user can create multiple slices from typed start/end timestamps.
- A user can set slice start/end from current playhead location.
- A user can preview and edit the slice list.
- A user can export each slice as a separate video file.
- A user can download all slices as a ZIP bundle.
- Frame-accurate slicing is the default export behavior.
- Projects and slice lists persist locally without login/cloud storage.
- Basic edit settings are available before export.
- The UI clearly reports export progress and errors.
