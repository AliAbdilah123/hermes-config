# Data-backed mobile search verification

## Acceptance setup

Use the user-named viewport exactly (for example 431 × 820). Verify both the static shell and the post-fetch settled state.

## Recipe

1. Request the public list API directly and confirm HTTP 200 plus a populated payload.
2. Request the public page with a cache-busting query.
3. Capture once immediately only to inspect the loading state.
4. Capture again with enough virtual-time budget (around 10 seconds) for hydration and API completion.
5. Inspect the settled image for:
   - the complete requested first row;
   - correct shared card anatomy;
   - loaded images or deliberate placeholders, never broken-image alt-text overlap;
   - fixed controls that remain outside horizontal scrollers;
   - no page-level horizontal overflow;
   - sufficient component spacing without violating the first-viewport target.
6. Open the filter surface and exercise draft edit → Cancel, draft edit → Apply, backdrop, Escape, Clear all, focus trap, and focus restoration.
7. Repeat the primary view in light and dark themes when supported, and inspect browser console output.
8. Confirm deployed `index.html` and asset hashes/timestamps correspond to the new build.

## Reporting

Report targeted changed-file lint separately from repository-wide lint. Give exact passed test counts/commands, build result, any pre-existing unrelated failures, commit SHA, upstream synchronization, deployment path, and public URL. Never summarize a partial suite as “all tests passed.”
