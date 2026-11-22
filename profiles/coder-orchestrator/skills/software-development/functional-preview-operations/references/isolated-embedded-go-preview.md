# Isolated embedded-Go application preview

Use for a Go binary that embeds its frontend and serves UI plus JSON API from one root-mounted process.

## Minimal durable pattern

1. Deploy a clean committed worktree at the exact feature SHA. Do not run the shared preview from a dirty production checkout.
2. Build the binary inside that worktree.
3. Create an isolated SQLite database with `VACUUM INTO` (or `.backup`) and require `PRAGMA integrity_check = ok` before startup.
4. Copy the runtime environment without printing secrets, then override only preview-specific values: unique loopback address, preview DB path, and any preview data roots.
5. Install a dedicated systemd unit with:
   - feature worktree as `WorkingDirectory`;
   - feature binary as `ExecStart`;
   - unique service name and loopback port;
   - isolated writable data path;
   - restart policy and boot enablement.
6. Add an exact nginx `server_name` for the feature hostname and proxy it to that unique port. Keep the production hostname/upstream unchanged.
7. Before nginx reload, run `nginx -t`. Long feature hostnames can exceed the existing names hash bucket; if nginx reports `could not build server_names_hash`, increase `server_names_hash_bucket_size` in the `http` block to the smallest sufficient value, test again, then reload.
8. Verify service ownership and identity, not just that a port answers:
   - `systemctl is-active <unit>`;
   - `ss -ltnp` shows the expected binary on the chosen port;
   - local API returns the application-specific JSON contract;
   - origin request with the intended `Host` header serves the feature assets.
9. Verify publicly with cache-busting queries:
   - deep route returns app HTML;
   - API returns JSON;
   - embedded JS/CSS return the correct MIME type;
   - HTML references the new asset version and semantic feature markers;
   - production still references its previous asset/version and remains isolated.
10. Recheck systemd activity immediately before sharing the link.

## Completion wording

HTTP/API/asset probes prove a durable public preview and transport isolation, but they do not prove interactive browser E2E. If browser automation is unavailable, say exactly that the preview is live and publicly probed, while click-through E2E remains unverified. Do not label the interaction itself “publicly verified.”

## Cleanup inventory

Record the worktree path, service unit, port, nginx config, database path, and hostname so rejection or approval can cleanly remove or promote the preview without guessing.
