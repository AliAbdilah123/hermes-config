# Branched job-detail modal overflow

Conversation branches can add long session IDs, branch titles, summaries, URLs, and timestamps to a job inspector. These are untrusted-width values and can force a modal beyond the viewport.

## Minimal fix pattern

- Bound the inspector with `max-width: 100vw`.
- Keep vertical scrolling (`overflow-y: auto`) and suppress horizontal spill (`overflow-x: hidden`).
- Set `min-width: 0` on nested grid/flex sections and the dialog body.
- Wrap branch metadata with `overflow-wrap: anywhere` and `word-break: break-word`.
- Verify with a real branched-job payload, not only a normal job.

In a dirty repository, stage only the exact CSS/component file changed; preserve unrelated source and documentation changes.