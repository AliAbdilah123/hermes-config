# Optimistic full-stack mutations

Use this checklist when adding a versioned mutation that spans SQL, store, HTTP, and an embedded frontend.

1. Write RED tests first for the successful roundtrip, stale-version rejection, domain preconditions, and HTTP status/body behavior. Capture the expected failure before production edits.
2. Persist structured fields explicitly rather than hiding operational evidence in one opaque string. Return them from detail reads and expose them in the editor.
3. Apply the optimistic guard in SQL (`WHERE id=? AND version=?`) and require `RowsAffected()==1`; a prior version read alone does not close the race.
4. Keep the evidence update and version increment in one transaction. Trim boundary text where blank/nonblank semantics matter.
5. Enforce terminal-state prerequisites in the store transition, not only in the UI. Example: completion requires a nonblank verification summary.
6. Update all status surfaces together: transition map, frontend actions, active-resource uniqueness assumptions, and cancellation paths.
7. Avoid semantic overclaiming in summaries. An ordered plan's first item is “Plan starts with,” not necessarily the “next” action after execution has begun.
8. For literal CSS selectors in a stylesheet, use CSS quotes directly (`[aria-current="page"]`); do not retain JavaScript/string escaping (`\"`) in the emitted CSS.
9. Verify every changed layer after the final edit: uncached store/API tests, vet, production build, JS syntax, CSS positive/negative literal assertions, and `git diff --check`. If workspace metadata still says unverified, run the temporary ad-hoc verifier described in `ad-hoc-verification-evidence.md` and call it ad-hoc evidence rather than suite green.
10. In a dirty worktree, modify only requested tracked files and the current feature assets/docs; leave unrelated untracked plans and documents untouched.
