# Final sequential verification gate

Use this after all edits and immediately before commit or completion.

1. Run the complete relevant check chain sequentially against the final workspace: focused/backend tests, full frontend tests, typecheck, lint, build, and `git diff --check` as applicable.
2. Treat focused or parallel checks as feedback, not final evidence. Competing suites can create false timeouts; later edits make earlier passes stale.
3. If a parallel run times out but an unloaded rerun passes, rerun the full affected suite cleanly. Report both the timeout and the clean pass rather than diagnosing a product defect from contention.
4. Report lint precisely: `0 errors, N warnings` may pass when warnings are permitted, but warning-bearing output is not pristine.
5. Inspect `git status`; stage only task-owned paths and preserve unrelated modified or untracked files.
6. After push, verify the intended commit and branch synchronization separately.

A single successful sequential chain is the clearest completion evidence and avoids repeated verification prompts caused by fragmented or stale results.
