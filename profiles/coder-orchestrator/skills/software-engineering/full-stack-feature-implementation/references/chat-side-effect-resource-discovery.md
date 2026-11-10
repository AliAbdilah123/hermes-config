# Chat side effects that create discoverable resources

When an in-app AI chat can create a filesystem-backed resource that the application lists from a cache/index, successful chat completion is not enough. Reconcile the authoritative source into the application store before returning success, then refresh the visible collection in the client.

## Minimal implementation pattern

1. Trace the listing source end to end: chat action → authoritative artifact → scanner/indexer → store → list endpoint → rendered collection.
2. Write a focused failing API test first. Have the fake chat callback create the real discoverable artifact (for example, a project directory plus manifest) during chat completion, submit the chat request, and assert the store/list endpoint contains it.
3. After every successful chat path that can mutate resources—both initial conversation creation and follow-up messages—run the existing scanner/indexer. Reuse the established discovery path rather than parsing assistant text or adding a second project-creation API.
4. Refresh the collection after the successful client reply so the resource appears without a page reload.
5. Keep chat success independent from optional presentation refresh failures where appropriate; decide explicitly whether reconciliation errors should fail the request or be surfaced as warnings.

## Pitfalls

- Updating only the first-message endpoint misses projects created in follow-up turns.
- Refreshing only the browser list cannot discover an artifact that has not been reconciled into the backend store.
- Backend reconciliation alone leaves the UI stale until reload.
- Do not infer creation from assistant prose; inspect the authoritative artifact through the existing scanner.
- In a dirty or concurrently edited repository, read the current file and preserve unrelated behavior when adding the refresh. A one-line addition to the latest function body is safer than replacing the whole function from an older snapshot.

## Verification

- Prove RED before production code.
- Run the focused test, then the full backend suite.
- Syntax-check the touched client asset and run the repository diff check.
- Confirm the final diff contains only the reconciliation, collection refresh, regression test, and required changelog entry.
