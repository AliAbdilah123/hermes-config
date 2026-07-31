# Preview mount persistence and checkpointing

Use this when a validated subpath preview later appears to regress or when its worktree accumulates several fixes.

## Prove the preview is still mounted before changing code

Fetch a cache-busted public preview URL and confirm:

1. The module asset URL contains the exact preview prefix.
2. `window.__BASENAME__` equals that prefix.
3. `window.__API_BASE__` equals `<preview-prefix>/api/v1`.
4. Nginx still has both the preview static location and preview API proxy.
5. The preview directory and `index.html` still exist.
6. Origin and public responses agree.

Root `/assets/...`, basename `/`, or API `/api/v1` means the URL has fallen through to the root app. Restore the isolated mount and artifact before diagnosing application logic. After Nginx reload, an internal-redirection cycle or HTTP 500 means the mount is not restored yet; verify `root`/`alias`, `try_files`, filesystem existence, and readability.

## Exact public acceptance

After restoring the mount, rerun the reported browser workflow. Tests and bundle-string checks prove code presence, not runtime behavior. For booking-origin commerce, prove all three outcomes:

- Existing eligible voucher: confirmation/custom fields → claim → focused My Bookings.
- No voucher: package checkout → automatic claim → focused My Bookings.
- Direct package purchase without session intent → Wallet.

## Checkpoint commits

Preview-only is not the same as uncommitted. Unless the user explicitly says not to commit:

- Commit validated source changes in logical groups as work accumulates.
- Exclude databases, generated binaries, uploads, `.env` files, and credentials.
- State whether commits are local or pushed.
- If an old task said “do not commit” but later work materially expands the dirty tree, ask whether it still applies instead of silently carrying it forever.

Checkpoint commits protect work from reset/overwrite; they do not imply production deployment or merge approval.
