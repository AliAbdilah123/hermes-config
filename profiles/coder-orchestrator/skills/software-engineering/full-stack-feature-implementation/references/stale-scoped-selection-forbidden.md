# Stale Scoped Selection Causing 403

Use when a create form gets `403 Forbidden` despite the signed-in user having at least one valid parent resource.

A form may prefer a parent ID from global state, a URL filter, local storage, or a prior edit. If that ID is not checked against the freshly fetched authorized resources, submission sends a stale or foreign ID and the API correctly rejects it.

## Diagnose

1. Preserve the backend authorization check; do not weaken it.
2. Compare the submitted parent ID with the authorized collection returned to that user.
3. Trace initialization and reset/add-another paths for stale IDs.
4. Treat fallback sentinel IDs such as `default` as suspect unless the backend guarantees ownership.

## Minimal fix

```ts
const preferredId = editValue?.parentId ?? globalFilterId
setSelectedId(
  authorizedParents.some(({ id }) => id === preferredId)
    ? preferredId ?? null
    : authorizedParents[0]?.id ?? null
)
```

If the authorized collection is empty, fail closed and disable submission with useful copy.

## Verify

- A stale preferred ID falls back to an authorized resource.
- A valid preferred ID remains selected.
- An empty authorized collection cannot submit.
- Public/API E2E: fresh user → fetch authorized parent → create child → success.
- A deliberately foreign parent still returns 403, proving server authorization remains intact.
