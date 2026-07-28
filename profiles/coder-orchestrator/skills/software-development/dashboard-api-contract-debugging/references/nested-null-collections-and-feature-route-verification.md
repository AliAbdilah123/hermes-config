# Nested null collections and exact-route verification

## Failure pattern

A dashboard can normalize endpoint envelopes correctly and still crash later:

```ts
const members = items(memberResponse) // protects data/items being null
members.flatMap(member => member.roles.filter(...)) // roles may still be null
```

Use nested normalization at the mapper boundary:

```ts
(member.roles ?? []).filter(...)
(template.weekly_slots ?? []).length
```

## Minimal RED fixture

Render the real route and return a realistic member with `roles: null`. Assert the page's expected heading/content appears and no alert is rendered. Before the fix, confirm the test fails with the exact `reading 'filter'` error.

Repeat for every candidate nested collection rather than combining all nulls in one fixture; isolated tests identify the actual contract violation.

## Preview verification split

### Infrastructure boundary

- Dedicated web-server location exists for the preview.
- SPA fallback returns preview index, not production index.
- Router basename and API base are correct.
- Hashed JS/CSS have correct MIME types.
- Headless browser renders expected generic app content and no `Page not found`.

### Feature boundary

- Navigate to the exact reported tab and role.
- Use a real authenticated session and runtime API response when possible.
- Confirm expected tab content appears and runtime/console errors are absent.
- If auth is unavailable, rely on the exact route-level regression test and state clearly that live authenticated feature verification is pending.

Never use landing-page rendering as evidence that an authenticated tab's data contract is fixed.

## Theme ownership check

For a request to move theme styling above tab containers:

- Shared dashboard shell owns light/dark tokens and full-page background.
- Tab/page scaffold inherits tokens and has a transparent background.
- Theme toggle location is a separate concern; do not mistake moving the control for moving theme ownership.
- Add a source/CSS assertion for both the new owner and removal from the old owner.
