# Photo crop file-switch race

Use this when a multi-image crop modal already stores state in `WeakMap<File, CropState>` but thumbnail clicks still jump back, mutate another image, or shrink a prior crop.

## Root cause

`WeakMap<File, CropState>` alone is insufficient. During a React `file` prop transition, the new `file` can render while `box`, `displayW`, and `displayH` still describe the old image. A persistence effect keyed by both `file` and geometry can therefore save the old normalized crop under the new `File` before its `<img onLoad>` runs.

A second race occurs when the parent calls `setPendingFile` or other setters from inside `setCropQueue(prev => ...)`. Batched updates and closed-over state can reactivate the wrong thumbnail.

## Minimal fix

1. Keep crop memory keyed by exact `File` identity.
2. Add `loadedFileRef: File | null` in the crop modal.
3. On every `file` change, set the marker to `null` and clear transient `displayW`, `displayH`, and crop box geometry before creating the new object URL.
4. In the persistence effect, return unless `loadedFileRef.current === file` and geometry is valid.
5. In the current image's load handler, set `loadedFileRef.current = file`, then restore that file's normalized box and output settings once.
6. Make thumbnail selection a pure deterministic transition: selected queued file becomes active; the previous active file is inserted exactly once into the queue; remove the selected queue entry. Apply the resulting active file and queue with direct setters—never setters nested inside another setter callback.

## Regression shape

- Start with active file A and queue `[B, C]`.
- Select B and assert active identity is exactly B and queue is `[A, C]`.
- Use two distinct `File` objects with identical name, size, and timestamp to prove identity isolation.
- Verify A → B → A restores A's exact normalized box, ratio, max-PX, and custom ratio fields without compounding display scaling.
- Run the focused crop tests, typecheck, and production build; after deployment verify the hashed crop chunk returns `application/javascript` and contains durable crop UI/state markers.

## Scope ceiling

Do not rewrite crop math, replace the cropper, or add a global editor store for this race. The loaded-file gate plus deterministic queue swap is the smallest fix.
