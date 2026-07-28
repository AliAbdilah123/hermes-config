# Payment preview promotion and production cleanup

Use after explicit approval of a snapshot-backed Komuna payment preview.

## Promote safely

1. Verify the approved branch is clean, pushed, and still based on the expected remote `master`.
2. If the production source checkout is dirty with unrelated work, do not reset, stash, or merge in it. Advance remote `master` from the clean approved worktree and build deployable artifacts there.
3. Before restart or migration, create a SQLite `.backup` of the live WAL database and back up the current API binary and frontend artifact.
4. Build the Go API and frontend from the exact approved commit, install the binary atomically, restart the actual systemd unit, and verify its loopback listener and logs.
5. Verify database integrity after startup (`PRAGMA quick_check`) and probe both loopback and public JSON APIs.

## Prove the browser, not just transport

A 200 response, valid JS syntax, or fresh entry hash does not prove the SPA starts. Open the public production URL in a real browser/CDP session and assert:

- `#root` has rendered content;
- expected route text appears;
- no uncaught JavaScript/module errors exist;
- every imported JS chunk has JavaScript MIME.

Cloudflare can cache stale HTML at an old generated module URL even when origin now serves JavaScript. The browser symptom is:

> Expected a JavaScript-or-Wasm module script but the server responded with a MIME type of `text/html`.

When this occurs, rebuild from a clean `dist`, rename **every generated JS chunk as one coordinated set**, rewrite all HTML and inter-chunk references before deployment, syntax-check all renamed chunks, deploy atomically, and browser-verify again. Never rename only the entry file; stale lazy/shared chunks can still blank the app.

## Retire the approved preview

Approval is also a cleanup gate. After production browser verification succeeds:

1. Remove every nginx location belonging to the preview (usually SPA and API locations), then run `nginx -t` and reload.
2. Stop the tracked preview API process and verify its loopback port is no longer listening.
3. Remove the preview frontend directory, snapshot database, preview binary, and preview-only fixtures/backups.
4. Verify the exact preview directory and nginx markers are absent. Do not use HTTP 404 alone: the production SPA fallback may return 200, and a broken stale route may return 500.
5. Re-check production after cleanup.

## Provider-backed preview fixtures

If a genuine Xendit test invoice was created only to review `Complete payment`, retain its provider invoice ID independently of the disposable SQLite row. On cleanup, attempt provider cancellation/expiration using the provider-supported endpoint and verify provider status. Then remove the preview-only purchase/items from the snapshot. Never leave a fake hosted-checkout URL or describe a placeholder as functional.
