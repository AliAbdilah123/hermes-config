# Edit & Retry media replacement cancel should restore previous media

When fixing SocialZen Edit & Retry media flows, distinguish three states:

- `keep`: old persisted media remains selected and visible.
- `replace`: user is intentionally replacing media and must provide/upload new media before save.
- crop modal open: a temporary pending file is being edited before it becomes replacement media.

Bug pattern: setting `mediaMode = "replace"` before the crop/upload completes, then making Crop Cancel/X/backdrop only clear `pendingFile` leaves the form in `replace` with `newMedia = []`. The old media appears deleted and Save shows “choose new media” even though the user cancelled.

Fix pattern:

1. Add one shared “use previous media” action that sets `mediaMode` back to `keep`, clears `newMedia`, and clears upload progress/input state.
2. Route all cancel exits through it: crop modal Cancel/X, backdrop/outside-card click, and the explicit form button.
3. Keep Apply separate: Apply may upload/advance the crop queue; Cancel must never upload or leave replacement mode active.
4. Add a small regression around the state reset helper or UI behavior.
5. Verify the deployed EditPostPage bundle contains the exact user-facing copy.

User-facing copy requested for the explicit button under Change media: `Cancel and use previous media.`
