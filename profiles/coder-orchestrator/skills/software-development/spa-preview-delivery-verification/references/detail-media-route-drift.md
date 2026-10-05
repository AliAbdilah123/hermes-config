# Detail Media Route Drift

Use when cached media exists and its protected endpoint works, but image/video elements on a nested SPA detail route remain blank.

## Diagnosis

1. Confirm attachment metadata is present.
2. Confirm cache state is available and the file is non-empty.
3. Read the frontend helper constructing `src`.
4. Evaluate it with a real nested page base such as `/notes/46`.
5. Probe both the generated URL and intended API URL, checking MIME/body—not status alone.

Relative construction such as:

```ts
new URL(`./api/notes/${id}/media/${key}`, document.baseURI).pathname
```

produces `/notes/api/...` from `/notes/46`. SPA fallback may return HTML with HTTP 200, disguising routing failure as broken media.

## Fix choice

- Root-mounted app with root API: emit `/api/...` explicitly.
- Subpath app: use the established base-aware API path helper.
- Always encode the media key.

## Regression and release proof

- Set `document.baseURI` to a nested detail URL and assert the resulting media path.
- Include spaces or another encoding-sensitive character in the key.
- Observe RED, apply the smallest helper change, then run full frontend tests, type/Svelte checks, and build.
- Inspect the publicly served bundle for the corrected path.
- Perform authenticated owner-scoped E2E when credentials exist. If the available account does not own the record, do not mutate ownership or credentials; report the limitation and keep bundle/endpoint evidence scoped accurately.
