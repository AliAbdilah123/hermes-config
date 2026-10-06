# Cross-layer list/filter verification

Use this for features that add persisted metadata, list filters, bulk actions, or a new supporting endpoint across DB → API → frontend.

## Contract trace

For every requirement, trace one executable path end-to-end:

1. **Write path:** every producer (manual create/update, webhook/social ingestion, split-event completion) writes the same derived state transactionally.
2. **Read path:** detail and list DTOs expose the state consistently.
3. **Discovery path:** filter-option data comes from the full authenticated user dataset, not merely the current page of results.
4. **Filter path:** URL/query serialization, API parsing/validation, parameterized SQL, ownership scope, pagination count, and UI restoration agree.
5. **Action path:** destructive bulk actions preserve failed selections and clearly define whether “all” means visible page or full result set.

## Common false-positive completion

A backend endpoint may exist and pass tests while the UI never calls it. After implementation, search/inspect both the route registration and its frontend consumer, then exercise the deployed request. For tag/source selectors, test a tag that exists only on a note outside page 1; it must still appear as an available filter.

Likewise, source assertions against generated assets prove deployment, not interaction. Distinguish:

- build/source tests,
- deployed asset markers,
- authenticated public API E2E,
- browser UI E2E.

Never report browser E2E unless a browser actually completed the user flow. If browser automation is unavailable, report the narrower evidence honestly and keep READY gated when the acceptance contract explicitly requires UI E2E.

## Minimal verification matrix

- Create body with mixed-case/Unicode hashtags; verify normalized dedupe and display spelling.
- Edit body; verify removed tags disappear from that note and shared tags remain for other notes.
- Put a unique tag beyond page 1; verify the filter option is still discoverable.
- Combine title/body query + multiple sources + multiple tags; verify ownership and total count.
- Open social-note detail; verify no resolver/provider request occurs before explicit activation.
- Export selected visible notes in visible order.
- Force one delete failure; verify successful deletions disappear and failed IDs remain selected.
