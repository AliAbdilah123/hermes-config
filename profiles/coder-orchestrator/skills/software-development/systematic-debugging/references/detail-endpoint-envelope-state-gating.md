# Detail endpoint envelopes can hide state-gated controls

## Symptom pattern

A list/card correctly shows an entity's task, status, and tool, but its detail modal shows blank metadata such as `· · attempt`, while a sibling collection such as timeline events still renders. Controls gated by status (reply, retry, approve, edit) are unexpectedly absent.

## Root cause

The list endpoint returns a flat entity, while the detail endpoint returns an envelope such as:

```json
{"job": {"state": "blocked", "task": "..."}, "events": [...]}
```

The modal stores the whole response as the entity and reads `response.state` instead of `response.job.state`. Since the state is `undefined`, conditions such as `canComment(state)` return false and hide otherwise-valid controls.

## Investigation recipe

1. Compare the card's runtime data with the detail endpoint's real JSON.
2. Treat partially working detail content as evidence of shape drift, not missing database values.
3. Inspect blank interpolation landmarks (`· · attempt`) and status-gated rendering conditions.
4. Confirm authoritative database values only to rule out data loss; do not patch the database.

## Minimal fix

Normalize once at the detail API boundary and preserve sibling fields:

```ts
export const normalizeDetail = (response: DetailResponse) => ({
  ...response.job,
  events: response.events,
})
```

Use the same normalizer for initial load, SSE-triggered reloads, and post-action refreshes. Fixing only initial load causes the modal to regress after sending a comment or receiving an event.

## Regression check

Write a test first with a realistic enveloped response. Assert that normalization exposes the status and retains timeline events. Then verify the production build's detail modal displays metadata and the status-gated control for an eligible state.

## Deployment verification

A bundle marker only proves code presence, not correct rendering. Verify:

- the served HTML references the newly built hashed asset;
- the served asset contains the expected UI marker;
- the running service serves that asset;
- ideally, authenticated rendered DOM shows the entity metadata and gated control.
