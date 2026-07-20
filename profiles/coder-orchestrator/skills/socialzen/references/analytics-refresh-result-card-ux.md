# Analytics refresh-result card UX

Use when implementing the approved SocialZen Analytics refresh-result summary/details experience.

## Contract

Refresh counts are mutually exclusive and count attempted published destinations (post targets):

- `success`: every requested metric refreshed
- `partial_success`: basic metrics persisted but one or more insight calls failed
- `failed`: no usable metric refresh succeeded

Return safe, UI-ready results per destination:

```ts
{
  platform: 'instagram' | 'facebook' | 'threads',
  accountDisplay: '@username' | 'Page name',
  status: 'success' | 'partial_success' | 'failed',
  refreshedMetrics: string[],
  unavailableMetrics: string[],
  reason: '' | 'Unsupported by platform' | 'Meta did not return this metric' |
    'Permission expired' | 'Account disconnected' | 'Refresh failed' |
    'Provider service error',
  action: '' | 'reconnect' | 'retry'
}
```

Never expose `post_target_id`, raw provider errors, tokens, or internal wording such as “platform target” in the UI. Map provider errors to a small controlled reason/action vocabulary; keep raw redacted diagnostics in server logs.

## UI

Render a responsive result card after refresh:

1. Heading: `Analytics refresh completed` or `Analytics refresh completed with some issues`.
2. Four stats: Checked destinations, Fully refreshed, Partially refreshed, Failed.
3. Collapsed `View details` control.
4. Expanded cards grouped by `Platform · accountDisplay`, showing status, refreshed metrics, unavailable metrics, reason, and only the applicable Reconnect/Try again action.
5. Keep stale analytics visible; reload overview only when at least one destination produced usable data.

For unavailable post-detail metrics, preserve `null` vs confirmed `0`. Show a reason only when supported by capability or refresh evidence:

- Facebook/Threads Saves: `Unsupported by platform`.
- Provider omitted a supported metric: `Meta did not return this metric` only when refresh evidence says so.
- Do not guess a reason from `null` alone.

Rename the vague `What Worked` section to `Content Performance Insights`, with the subtitle `Patterns from your best-performing posts.` Keep its cards linked to the existing post-detail modal.

## Scope and verification

If refresh accepts `account_id`, enforce it in the backend query; otherwise the UI control is misleading.

TDD checks should cover:

- exclusive aggregate counts
- controlled safe error mapping
- no internal destination IDs in rendered output
- expandable destination details and reconnect action
- capability/evidence-based unavailable reasons
- renamed insights heading/subtitle

Run focused frontend analytics tests, TypeScript typecheck, production frontend build, focused Go analytics tests, and Go build. Deploy the hashed Analytics chunk and verify its content type plus distinctive markers (`Checked destinations`, `Content Performance Insights`). Visual verification still requires a settled authenticated browser render; bundle markers and component tests are supporting evidence, not a substitute for a screenshot/DOM inspection.
