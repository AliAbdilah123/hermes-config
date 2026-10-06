# Webhook-free cross-provider comment workflows

Use when auditing, planning, or implementing Facebook, Instagram, or Threads comments/replies in SocialZen.

## Interpret audit intent before proposing fixes

When the user asks to audit one provider's working comment logic while discussing another provider, first determine whether the working provider is intended as a **reference architecture**. Do not default to proposing improvements to the audited provider. State the transfer target explicitly:

- reference provider and behavior;
- destination provider(s);
- reusable mechanism;
- provider-specific differences requiring separate handling.

If multiple destination providers are requested, produce separate provider plans when their API semantics, permissions, or mutation support differ. A combined overview may link them, but should not replace them.

## Shared reference architecture

Comments do not inherently require webhooks. A complete pull-based workflow can use:

1. Resolve the authenticated owner's exact published `post_target`.
2. Resolve the exact connected account and unexpired provider token.
3. Use `post_targets.platform_post_id` as the provider object/media ID.
4. Cursor-page the provider's top-level comments/replies edge.
5. Separately cursor-page each supported child-reply edge.
6. Upsert provider IDs into `provider_comments`, preserving both local `parent_id` and provider parent ID.
7. Render cached rows immediately; run one provider refresh on drawer open; reload local pages afterward; retain manual Refresh.
8. Treat webhooks as optional acceleration, not a prerequisite.

For mutations, record a delivery attempt, call the provider synchronously, and persist the local comment only after a confirmed provider ID. Keep `DELIVERED`, `FAILED`, and `UNKNOWN` distinct. Never copy legacy local-first behavior that reports success before provider confirmation.

## Provider distinctions

### Instagram

- Top-level: `/{media-id}/comments`.
- Replies: `/{comment-id}/replies`.
- Useful as the reference model, but its edge names and permissions must not be copied blindly.

### Facebook Pages

- Top-level Page-post comments: `/{post-id}/comments`.
- Replies: `/{comment-id}/comments`.
- Resolve the exact Page and Page token.
- Reading, Page-authored mutation, and moderation can require different permissions and ownership checks.
- Edit/delete capability must be verified for the active Graph version and comment ownership class.

### Threads

- Product terminology is **replies**.
- Initial read commonly begins at `/{threads-media-id}/replies`; verify supported child/conversation edges against the active Threads API rather than inferring Instagram parity.
- Use a direct Threads account/token, not Instagram or Facebook credentials.
- Enforce the provider's Unicode text limit at frontend and backend boundaries.
- Publishing may require create-container, status polling, and publish; persist only the final provider reply ID.
- Do not promise edit/delete parity unless the current official API supports it.

## Pagination and reconciliation safety

- Follow all parent and child cursors.
- Validate pagination scheme/host, reject userinfo and loops, and cap total pages.
- Propagate child-edge failures; a partial thread is not a successful refresh.
- Reconcile provider deletions only after every required page completes successfully.
- Never delete/tombstone local rows after partial, permission-denied, or transport-error syncs.

## Focused implementation verification

Add provider-channel tests that exercise the whole contract rather than isolated helpers:

- return multiple parent pages and multiple child pages, then assert provider IDs, local/provider parent mapping, and complete-sync reconciliation;
- return a malicious `paging.next`, assert only the trusted request ran, and prove pre-existing rows survive the failed partial sync;
- make frontend fetch mocks route by URL: refresh endpoints must return `{ provider: ... }`, while list endpoints return `{ comments, paging }`; one generic response can make the refresh fail before the required reload and conceal the actual drawer-open sequence;
- for cached-load → refresh → reload behavior, wait for two list calls and assert the refresh call independently instead of relying on a fixed number of resolved microtasks.

Before editing, record `git status --short` and `git rev-parse HEAD`. Re-check both before reporting. If HEAD or tracked files change concurrently, inspect the new commit/diff, avoid overwriting it, and distinguish paths changed by this run from paths already landed by another process. Never claim that you created or preserved a commit merely because it appeared during the session.

## Planning output

A detailed provider plan should include:

- channel/account/token resolution;
- exact read and reply edges;
- fields and pagination behavior;
- local/provider identity mapping;
- create/reply/update/delete sequencing;
- provider-specific capability rules;
- error classification and ambiguous-delivery behavior;
- deletion reconciliation;
- focused tests and authenticated public E2E;
- explicit statement that webhook configuration is not part of acceptance.

Keep implementation gated when the user asked for a plan. For separate Facebook and Threads requests, publish two independently reviewable plans rather than one blended document.
