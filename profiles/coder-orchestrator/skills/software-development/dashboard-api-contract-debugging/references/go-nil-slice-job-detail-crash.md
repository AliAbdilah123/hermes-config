# Go nil-slice detail response causing React blank screen

## Symptom

Opening an otherwise valid detail view—especially a queued/todo record with no child history—blanks the React screen with `TypeError: <minified variable> is not iterable`. A nearby 404 may be incidental rather than the render-crash cause.

## Root cause pattern

A Go handler declares a collection with a nil slice:

```go
var events []map[string]any
```

When no rows are appended, `encoding/json` emits `"events": null`. TypeScript types and default parameters do not make the runtime value iterable: `function Timeline({ events = [] })` only defaults `undefined`, not explicit `null`. Passing the value into `for...of`, `.map`, or `.filter` crashes rendering.

## Minimal two-boundary fix

1. Stabilize the server contract:

```go
events := []map[string]any{}
```

2. Normalize at the frontend API-to-view-model boundary, not throughout JSX:

```ts
{ ...payload.job, events: payload.events ?? [] }
```

Both are useful: the backend gives every client a correct contract; the frontend remains safe against stale deployments, caches, or older responses.

## TDD recipe

Backend RED test:

- Create a todo/queued record with no run or event rows.
- Request its real detail endpoint.
- Decode the `events` field as `json.RawMessage` and require the literal JSON array `[]`; merely unmarshalling into a Go slice can hide the `null` versus `[]` distinction.

Frontend RED test:

- Feed the detail normalizer both `null` and `undefined` events.
- Require the normalized value to equal `[]`.
- Render the actual timeline/detail component and assert the expected empty/queued state appears without throwing.

## Verification boundaries

Run the focused backend and frontend regressions, broader suites, and production build. For deployed work, verify the served bundle contains the nullish normalization and the API returns `[]`, but do not call this exact public E2E until an authenticated browser actually opens a no-event card and the console remains free of the iterable error. Report browser blockage separately from implementation/deployment success.
