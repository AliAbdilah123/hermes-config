# Comment manual refresh and provider status

Use when SocialZen's comments UI needs an explicit refresh action with honest Instagram/Facebook outcomes while preserving cached GET behavior.

## Contract

- Keep `GET /api/instagram/comments/:postId` cache-first and non-blocking: start provider sync in a goroutine, then immediately return local rows.
- Add a separate authenticated `POST /api/instagram/comments/:postId/refresh` for manual refresh. This endpoint waits for both provider sync attempts and returns per-provider statuses.
- After the POST resolves, the frontend must reload **all** local pages before replacing state. Do not treat the POST payload as the comment list.
- Keep mounted-drawer polling and the short post-open reload; manual refresh supplements rather than replaces them.

Suggested status shape:

```json
{
  "providers": [
    {"provider":"instagram","state":"ok|empty|error|unavailable","message":"..."},
    {"provider":"facebook","state":"ok|empty|error|unavailable","message":"..."}
  ]
}
```

Meanings:

- `ok`: provider fetch completed and returned at least one top-level comment.
- `empty`: provider fetch completed successfully with `data: []`; show this explicitly so empty is not confused with failure.
- `error`: target exists, but credentials/client/Graph fetch or parsing failed; return safe actionable copy, never token-bearing/raw Graph details.
- `unavailable`: the post has no eligible published target/provider media ID; normally omit this from warning UI.

## TDD sequence

1. Backend RED: fake Instagram returns an empty page and Facebook returns an HTTP error; assert ordered provider-specific `empty` and `error` statuses with visible messages.
2. Frontend RED: click the accessible `Refresh comments` button; assert refresh POST occurs before page reload, both provider messages render, and two local pages remain visible.
3. Drawer RED: assert the opened dialog uses the approved larger responsive width.
4. Implement the minimum endpoint/status propagation/UI.
5. Run focused backend comments tests, focused frontend component tests, typecheck, backend build, and frontend build.

## Pitfalls

- Returning no status from provider sync leaves Graph failures only in server logs and makes an empty UI ambiguous.
- Making GET wait for provider calls regresses cached/async responsiveness.
- Reloading only offset zero after manual refresh hides older top-level comments.
- A passing component test with React `act(...)` warnings is not pristine GREEN; wrap the click and its async state updates in `await act(async () => ...)`.
- Keep replies auto-expanded after every reload so synchronized replies are visible without another click.
