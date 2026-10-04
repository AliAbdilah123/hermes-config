# Complete social-provider enablement

Use when finishing or re-enabling a provider such as Threads across SocialZen. A provider may already have schema, OAuth helpers, metrics, and display support while still being deliberately blocked in routing, target validation, or UI selection.

## End-to-end audit

1. **Establish the baseline before editing**
   - Run `git status --short --branch` and preserve unrelated modified/untracked files.
   - Search the provider name across Go and TypeScript, including tests.
   - Look specifically for negative gates: `disabled`, `unsupported`, `not supported`, provider allowlists, omitted route cases, filtered platform arrays, and state resets that force the provider selection to empty.

2. **Connection lifecycle**
   - Register OAuth start and callback aliases in backend routing.
   - Confirm OAuth scopes cover profile, publishing, replies, and insights actually exposed by the product.
   - Verify account upsert/reconnect, list, disconnect, token expiry, and Settings success/error feedback.
   - In frontend Settings, load provider accounts and include the provider card rather than merely retaining dormant configuration.

3. **Composer and project lifecycle**
   - Include the provider in account fetching, connected-platform computation, destination controls, remembered selections, target payload construction, duplicate/edit hydration, and stale-account filtering.
   - Check both regular posts and Projects; SocialZen has multiple creation/edit paths.
   - Keep platform-specific media and caption limits at the trust boundary as well as in UI hints.

4. **Backend target contract**
   - Accept the provider in both explicit `targets` and legacy `platforms` payloads.
   - Validate account ownership, active status, token presence/expiry, provider identity snapshots, preflight, and retry/edit flows.
   - Ensure migrations and constraints accept the provider in every shared table used by publishing or comments.

5. **Publishing implementation**
   - Use the provider's actual publish protocol. Threads uses a create-container request followed by a publish request; replies also use a reply container then publish.
   - Cover text and every media type claimed by the UI. Return stable provider post IDs and propagate safe classified errors.
   - Preserve idempotency and publication-run state transitions already used by the shared publisher.

6. **Comments and analytics**
   - Include published targets in comment-channel discovery and resolve the correct provider account ID/token.
   - Sync top-level replies and nested replies using provider-specific fields, pagination, and graph base URL.
   - Enforce provider-specific reply limits (Threads: 500 Unicode characters) in backend and UI.
   - Verify metrics refresh, account labels, calendar/dashboard display, exports, and notifications.

## Test-first sequence

Convert intentional-disable tests into desired enablement tests first and observe them fail for the expected gate. Add focused tests for:

- OAuth start route availability.
- Explicit and legacy target creation.
- Provider publish protocol request bodies and returned ID.
- Reply publishing and provider-specific length limits.
- Account/settings and composer selection persistence.

Then implement the smallest cross-layer changes that make those tests pass.

## Verification

Run focused tests first, then canonical package/suite commands separately:

```bash
cd apps/backend-go
go test ./internal/threads ./internal/comments ./internal/posts
go test . -run 'TestThreads|TestCreatePostAcceptsExplicitThreadsTarget|TestCreateThreadsPostWithLegacyTargetFields'
go test ./...

cd ../frontend
pnpm exec vitest run src/pages/settings/SettingsPage.test.tsx src/pages/posts/CreatePostPage.test.ts src/components/comments/CommentList.test.tsx
pnpm test
pnpm build

cd ../..
git diff --check
git status --short
```

Do not assume `pnpm test -- --run ...` scopes Vitest; in this workspace it can invoke the full suite. Use `pnpm exec vitest run <files>` for focused frontend evidence.

## Reporting boundaries

- Distinguish focused pass, production build pass, and unrelated full-suite failures.
- Do not claim authenticated provider E2E without real OAuth credentials and a live provider account.
- Do not list files as changed unless confirmed by final `git status`/diff.
- Never include the tracked SQLite database or unrelated plans/docs in the feature diff unless explicitly required.
