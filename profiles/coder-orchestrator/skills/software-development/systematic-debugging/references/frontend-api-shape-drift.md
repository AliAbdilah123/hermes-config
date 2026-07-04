# Frontend/API Shape Drift: `.filter is not a function`

Use this when a React/Vite page renders an error like `x.filter is not a function`, `x.map is not a function`, or similar collection-method failures after an API call.

## Durable lesson

Do not assume the frontend TypeScript generic matches the deployed API shape. A common mismatch is:

- Frontend expects: `BookingDTO[]`
- API returns: `{ data: BookingDTO[] }` or another paginated/list envelope

The runtime value is an object, so array methods fail even though TypeScript compiled.

## Debug recipe

1. Find the throwing component and the array method call (`filter`, `map`, `flatMap`, `length` assumptions).
2. Trace the value to its `apiClient.get<T>()` call.
3. Probe the actual endpoint with curl or browser network evidence and inspect the JSON top-level shape.
4. Compare with working endpoints/tests in the codebase: some list endpoints return raw arrays, others return `{ data, meta }` or `{ data }`.
5. Fix at the response boundary with a typed normalizer/unwrap helper, not by sprinkling guards around every `.filter()` call.
6. Add a regression test using the real API shape that previously failed.
7. Verify both the targeted test and production build; if deployed, fetch the served bundle/API to confirm the new normalizer is present and the endpoint still returns the enveloped shape.

## Minimal pattern

```ts
type ListResponse<T> = T[] | { data: T[] }

function unwrapListResponse<T>(response: ListResponse<T>): T[] {
  return Array.isArray(response) ? response : response.data
}
```

Use a more specific name when the page only consumes one resource (for example `unwrapBookingsResponse`).

## Go nil slices → JSON `null` (not `[]`)

When a Go API returns paginated results with an `items` field, a nil slice (`var items []any`) marshals to JSON `null` instead of `[]`. Any frontend code that accesses `.items.length` or spreads `...items` will crash with `TypeError`.

**Root cause:** `var items []any` is nil (zero value). Appending in a loop that runs zero times leaves it nil. Go's `json.Marshal` encodes a nil slice as `null`.

**Fix:** Initialize slices: `items := []any{}` (or `items := make([]any, 0)`). Empty non-nil slices marshal to `[]`.

**Symptoms:**
- Page goes blank on a filtered view that returns zero results (e.g., `status=ongoing` tab with no ongoing sessions)
- Console shows `TypeError: Cannot read properties of null (reading 'length')` or `...null is not iterable`
- Working tabs return non-empty arrays fine; only zero-result filters crash
- "Blank page curse" follows to other tabs because React unmounts after an uncaught render error

**Verification:**
```bash
curl -s 'API?status=ongoing&page=1' | python3 -c "import json,sys;d=json.load(sys.stdin);print('null' if d.get('items') is None else f'[{len(d[\"items\"])}]')"
```

## Pitfalls

- `apiClient.get<MyDTO[]>('/endpoint')` is only a compile-time assertion; it does not validate runtime JSON.
- A test mock returning a raw array can hide a deployed API returning `{ data: [...] }`.
- Fixing the symptom by changing `.filter` to optional chaining can mask bad data and produce blank UI instead of accurate activity/statistics.
- Go nil slice → JSON `null` affects any endpoint that conditionally appends to a slice and returns it in a response envelope.
