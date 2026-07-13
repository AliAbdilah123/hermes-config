# Go JSON nil slices causing SPA crashes

## Symptom

A React/Vite SPA works before login, but after login shows a black/blank screen with no obvious server error. It often happens for fresh users, empty workspaces, or empty projects.

## Root cause pattern

Go encodes a nil slice as JSON `null`, not `[]`:

```go
var xs []Project
writeJSON(w, xs) // -> null when empty
```

Frontend code often assumes list endpoints return arrays:

```ts
api('/api/workspaces/w1/projects').then((ps) => {
  setProjects(ps)
  setProjectId(ps[0]?.id || '')
})

projects.map(...)
```

If the endpoint returns `null`, the first `ps[0]` or later `.map()`/`.filter()` crashes the render path, producing a blank SPA after auth.

## Investigation recipe

1. Reproduce with a fresh account or workspace that has no child records.
2. Probe the list endpoint directly and check whether the body is `null` instead of `[]`.
3. Inspect frontend boundaries for array assumptions: `ps[0]`, `.map`, `.filter`, `.length`.
4. Check Go handlers for `var xs []T` followed by append-loop and JSON write.

## Smallest durable fix

Initialize response slices before append loops so empty results encode as arrays:

```go
xs := []Project{}
for rows.Next() {
  var p Project
  // scan...
  xs = append(xs, p)
}
writeJSON(w, xs)
```

Apply to every collection field in API contracts, including nested DTO fields:

```go
d := Diagram{Nodes: []Node{}, Edges: []Edge{}}
```

Frontend can also normalize at the API boundary, but backend should still honor the array contract.

## Regression test

Add a focused test for the actual empty state:

- backend: empty list endpoint returns `[]`, not `null`.
- frontend: logged-in empty-project response renders the empty/create-project state and does not throw.
